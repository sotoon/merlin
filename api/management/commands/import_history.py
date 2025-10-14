import json
from typing import Dict, Optional

from django.core.management.base import BaseCommand
from django.db import transaction

from api.management.commands._import_utils import (
    average_or_none,
    normalize_stage,
    open_csv,
    parse_date,
    parse_float_or_none,
    parse_json_dict,
    row_savepoint,
    to_jsonl,
)
from api.models import TimelineEvent
from api.models.performance_tables import CompensationSnapshot, SenioritySnapshot
from api.models.ladder import Ladder
from api.models.organization import PayBand
from api.models.user import User


class Command(BaseCommand):
    help = "Import historical events and related snapshots. Does NOT touch org assignments."

    def add_arguments(self, parser):
        parser.add_argument("--csv", required=True)
        parser.add_argument("--encoding", default="utf-8")
        parser.add_argument("--delimiter", default=",")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--log-file", default=None)

    def handle(self, *args, **options):
        # Django passes dest names without leading dashes
        csv_path = options["csv"]
        encoding = options["encoding"]
        delimiter = options["delimiter"]
        dry_run = bool(options["dry_run"])
        log_path = options.get("log_file")

        def log(entry: Dict):
            if log_path:
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(to_jsonl(entry) + "\n")

        created_events = created_sen = created_comp = skipped = errors = 0

        with transaction.atomic():
            for idx, row in enumerate(open_csv(csv_path, encoding=encoding, delimiter=delimiter), start=2):
                row_errors = []
                warnings = []
                actions = {}

                user_email = (row.get("user_email") or "").strip()
                event_type = (row.get("event_type") or "").strip()
                summary_text = (row.get("summary_text") or "").strip()
                date_raw = (row.get("event_date") or "").strip()

                with row_savepoint(dry_run):
                    # Resolve user
                    user = User.objects.filter(email=user_email).first()
                    if not user:
                        row_errors.append(f"user not found: {user_email}")
                        errors += 1
                        log({"row": idx, "status": "error", "errors": row_errors})
                        continue

                    # Parse date
                    try:
                        effective_date = parse_date(date_raw)
                    except Exception:
                        row_errors.append(f"invalid date (expected YYYY-MM-DD): {date_raw}")
                        errors += 1
                        log({"row": idx, "status": "error", "errors": row_errors})
                        continue

                    # Generate rich summary text based on event type and available data
                    rich_summary = self._generate_rich_summary(row, event_type, user)
                    
                    # Check for existing events and handle duplicates properly
                    existing_events = TimelineEvent.objects.filter(
                        user=user,
                        event_type=event_type,
                        effective_date=effective_date,
                    ).order_by('-date_created')
                    
                    if existing_events.exists():
                        # If multiple events exist, delete all but the most recent
                        if existing_events.count() > 1:
                            events_to_delete = existing_events[1:]  # All except the first (most recent)
                            if not dry_run:
                                for event in events_to_delete:
                                    event.delete()
                            actions["timeline"] = f"cleaned-{len(events_to_delete)}-duplicates"
                        
                        # Update the remaining event with rich summary
                        latest_event = existing_events.first()
                        if not dry_run and latest_event.summary_text != rich_summary:
                            latest_event.summary_text = rich_summary or ""
                            latest_event.save(update_fields=['summary_text'])
                            actions["timeline"] = "updated"
                        else:
                            actions["timeline"] = "skipped-same"
                    else:
                        # Create TimelineEvent for ALL events, but without links (content_type=None, object_id=None)
                        if not dry_run:
                            TimelineEvent.objects.create(
                                user=user,
                                event_type=event_type,
                                summary_text=rich_summary or "",
                                effective_date=effective_date,
                                content_type=None,  # No links for imported events
                                object_id=None,     # No links for imported events
                                visibility_mask=1,
                                created_by=None,
                            )
                        created_events += 1
                        actions["timeline"] = "created"
                        
                        # Create Summary objects for committee events to ensure performance table calculations work
                        if event_type in {"MAPPING", "NOTICE", "SENIORITY_CHANGE", "EVALUATION"}:
                            if not dry_run:
                                from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                                
                                # Create or get the note
                                note, note_created = Note.objects.get_or_create(
                                    owner=user,
                                    title=rich_summary or f"{event_type} Event",
                                    content=rich_summary or "",
                                    date=effective_date,
                                    type="Proposal",
                                    proposal_type=ProposalType.EVALUATION,  # Use EVALUATION as default
                                    defaults={
                                        "content": rich_summary or "",
                                    }
                                )
                                
                                # Create or update the summary
                                summary, summary_created = Summary.objects.get_or_create(
                                    note=note,
                                    defaults={
                                        "content": rich_summary or "",
                                        "committee_date": effective_date,
                                        "submit_status": SummarySubmitStatus.DONE,
                                    }
                                )
                                
                                if not summary_created:
                                    # Update existing summary
                                    summary.committee_date = effective_date
                                    summary.submit_status = SummarySubmitStatus.DONE
                                    summary.save(update_fields=['committee_date', 'submit_status'])
                                
                                actions["summary"] = "created" if summary_created else "updated"
                            else:
                                actions["summary"] = "would-create"

                    # Per-event type: create snapshots
                    if event_type in {"SENIORITY_CHANGE", "MAPPING"}:
                        ladder_code = (row.get("ladder_code") or "").strip()
                        details = parse_json_dict(row.get("aspect_details_json"))
                        stages_raw = parse_json_dict(row.get("aspect_stages_json")) or {}
                        if not ladder_code:
                            row_errors.append("ladder_code required for this event type")
                        if not details:
                            row_errors.append("aspect_details_json required (absolute levels)")
                        ladder = Ladder.objects.filter(code=ladder_code).first() if ladder_code else None
                        if not ladder:
                            row_errors.append(f"ladder not found: {ladder_code}")

                        if row_errors:
                            errors += 1
                            log({"row": idx, "status": "error", "errors": row_errors, "actions": actions})
                            continue

                        # Normalize stages
                        stages = {k: normalize_stage(v) for k, v in stages_raw.items()}
                        overall_raw = (row.get("overall_score") or "").strip()
                        overall = None
                        try:
                            overall = float(overall_raw) if overall_raw else None
                        except Exception:
                            overall = None
                        if overall is None:
                            overall = average_or_none(details.values()) or 0.0

                        if not dry_run:
                            SenioritySnapshot.objects.create(
                                user=user,
                                ladder=ladder,
                                title=(row.get("performance_label") or row.get("ladder_title") or ""),
                                overall_score=overall,
                                details_json=details,
                                stages_json=stages,
                                effective_date=effective_date,
                                source_event=None,
                                is_redacted=False,
                            )
                        created_sen += 1
                        actions["seniority"] = "created"

                    elif event_type == "PAY_CHANGE":
                        pb_raw = (row.get("pay_band_number") or "").strip()
                        salary_change = parse_float_or_none(row.get("salary_change")) or 0.0
                        bonus_percentage = parse_float_or_none(row.get("bonus_percentage")) or 0.0

                        pay_band = None
                        if pb_raw:
                            try:
                                pb_num = float(pb_raw)
                            except Exception:
                                row_errors.append(f"invalid pay_band_number: {pb_raw}")
                                errors += 1
                                log({"row": idx, "status": "error", "errors": row_errors, "actions": actions})
                                continue
                            # Create/get PayBand
                            if not dry_run:
                                pay_band, _ = PayBand.objects.get_or_create(number=pb_num)
                            else:
                                pay_band = PayBand(number=pb_num)  # dummy instance for dry-run flow

                        if not dry_run:
                            CompensationSnapshot.objects.create(
                                user=user,
                                pay_band=pay_band,
                                salary_change=salary_change,
                                bonus_percentage=bonus_percentage,
                                effective_date=effective_date,
                                source_event=None,
                                is_redacted=False,
                            )
                        created_comp += 1
                        actions["compensation"] = "created"

                    elif event_type == "BONUS_PAYOUT":
                        bonus_percentage = parse_float_or_none(row.get("bonus_percentage"))
                        if bonus_percentage is None:
                            row_errors.append("bonus_percentage required for BONUS_PAYOUT")
                            errors += 1
                            log({"row": idx, "status": "error", "errors": row_errors, "actions": actions})
                            continue

                        # Carry forward latest pay band (if any) as-of date; do not change it
                        latest_comp = (
                            CompensationSnapshot.objects.filter(user=user, effective_date__lte=effective_date)
                            .order_by("-effective_date", "-date_created")
                            .first()
                        )

                        if not dry_run:
                            CompensationSnapshot.objects.create(
                                user=user,
                                pay_band=getattr(latest_comp, "pay_band", None),
                                salary_change=0.0,
                                bonus_percentage=bonus_percentage,
                                effective_date=effective_date,
                                source_event=None,
                                is_redacted=False,
                            )
                        created_comp += 1
                        actions["compensation"] = "created"

                    elif event_type == "EVALUATION":
                        # Create Summary object for committee calculations
                        if not dry_run:
                            from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                            
                            # Create or get the note
                            note, note_created = Note.objects.get_or_create(
                                owner=user,
                                title=rich_summary or "ارزیابی عملکرد",
                                content=rich_summary or "",
                                date=effective_date,
                                type="Proposal",
                                proposal_type=ProposalType.EVALUATION,
                                defaults={
                                    "content": rich_summary or "",
                                }
                            )
                            
                            # Create or update the summary
                            summary, summary_created = Summary.objects.get_or_create(
                                note=note,
                                defaults={
                                    "content": rich_summary or "",
                                    "committee_date": effective_date,
                                    "submit_status": SummarySubmitStatus.DONE,
                                }
                            )
                            
                            if not summary_created:
                                # Update existing summary
                                summary.committee_date = effective_date
                                summary.submit_status = SummarySubmitStatus.DONE
                                summary.save(update_fields=['committee_date', 'submit_status'])
                            
                            actions["summary"] = "created" if summary_created else "updated"
                        else:
                            actions["summary"] = "would-create"

                    elif event_type == "MAPPING":
                        # Create Summary object for committee calculations
                        if not dry_run:
                            from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                            
                            # Create or get the note
                            note, note_created = Note.objects.get_or_create(
                                owner=user,
                                title=rich_summary or "مپینگ لدر",
                                content=rich_summary or "",
                                date=effective_date,
                                type="Proposal",
                                proposal_type=ProposalType.MAPPING,
                                defaults={
                                    "content": rich_summary or "",
                                }
                            )
                            
                            # Create or update the summary
                            summary, summary_created = Summary.objects.get_or_create(
                                note=note,
                                defaults={
                                    "content": rich_summary or "",
                                    "committee_date": effective_date,
                                    "submit_status": SummarySubmitStatus.DONE,
                                }
                            )
                            
                            if not summary_created:
                                # Update existing summary
                                summary.committee_date = effective_date
                                summary.submit_status = SummarySubmitStatus.DONE
                                summary.save(update_fields=['committee_date', 'submit_status'])
                            
                            actions["summary"] = "created" if summary_created else "updated"
                        else:
                            actions["summary"] = "would-create"

                    elif event_type == "PROMOTION":
                        # Create Summary object for committee calculations
                        if not dry_run:
                            from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                            
                            # Create or get the note
                            note, note_created = Note.objects.get_or_create(
                                owner=user,
                                title=rich_summary or "ارتقا",
                                content=rich_summary or "",
                                date=effective_date,
                                type="Proposal",
                                proposal_type=ProposalType.PROMOTION,
                                defaults={
                                    "content": rich_summary or "",
                                }
                            )
                            
                            # Create or update the summary
                            summary, summary_created = Summary.objects.get_or_create(
                                note=note,
                                defaults={
                                    "content": rich_summary or "",
                                    "committee_date": effective_date,
                                    "submit_status": SummarySubmitStatus.DONE,
                                }
                            )
                            
                            if not summary_created:
                                # Update existing summary
                                summary.committee_date = effective_date
                                summary.submit_status = SummarySubmitStatus.DONE
                                summary.save(update_fields=['committee_date', 'submit_status'])
                            
                            actions["summary"] = "created" if summary_created else "updated"
                        else:
                            actions["summary"] = "would-create"

                    elif event_type == "SENIORITY_CHANGE":
                        # Create Summary object for committee calculations
                        if not dry_run:
                            from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                            
                            # Create or get the note
                            note, note_created = Note.objects.get_or_create(
                                owner=user,
                                title=rich_summary or "تغییر سطح لدر",
                                content=rich_summary or "",
                                date=effective_date,
                                type="Proposal",
                                proposal_type=ProposalType.EVALUATION,  # Use EVALUATION as closest match
                                defaults={
                                    "content": rich_summary or "",
                                }
                            )
                            
                            # Create or update the summary
                            summary, summary_created = Summary.objects.get_or_create(
                                note=note,
                                defaults={
                                    "content": rich_summary or "",
                                    "committee_date": effective_date,
                                    "submit_status": SummarySubmitStatus.DONE,
                                }
                            )
                            
                            if not summary_created:
                                # Update existing summary
                                summary.committee_date = effective_date
                                summary.submit_status = SummarySubmitStatus.DONE
                                summary.save(update_fields=['committee_date', 'submit_status'])
                            
                            actions["summary"] = "created" if summary_created else "updated"
                        else:
                            actions["summary"] = "would-create"

                    elif event_type == "NOTICE":
                        # Create Summary object for committee calculations
                        if not dry_run:
                            from api.models.note import Note, ProposalType, Summary, SummarySubmitStatus
                            
                            # Create or get the note
                            note, note_created = Note.objects.get_or_create(
                                owner=user,
                                title=rich_summary or "نوتیس عملکردی",
                                content=rich_summary or "",
                                date=effective_date,
                                type="Proposal",
                                proposal_type=ProposalType.EVALUATION,  # Use EVALUATION as closest match
                                defaults={
                                    "content": rich_summary or "",
                                }
                            )
                            
                            # Create or update the summary
                            summary, summary_created = Summary.objects.get_or_create(
                                note=note,
                                defaults={
                                    "content": rich_summary or "",
                                    "committee_date": effective_date,
                                    "submit_status": SummarySubmitStatus.DONE,
                                }
                            )
                            
                            if not summary_created:
                                # Update existing summary
                                summary.committee_date = effective_date
                                summary.submit_status = SummarySubmitStatus.DONE
                                summary.save(update_fields=['committee_date', 'submit_status'])
                            
                            actions["summary"] = "created" if summary_created else "updated"
                        else:
                            actions["summary"] = "would-create"

                    else:
                        warnings.append(f"unknown event_type: {event_type}")

                    log({"row": idx, "status": "ok" if not row_errors else "error", "actions": actions, "warnings": warnings, "errors": row_errors})

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry-run complete (no changes committed)."))
        self.stdout.write(self.style.SUCCESS(
            f"History import finished. events={created_events}, seniority_snaps={created_sen}, comp_snaps={created_comp}, errors={errors}"
        ))

    def _generate_rich_summary(self, row, event_type, user):
        """Generate rich summary text based on event type and available data, mimicking signals.py behavior."""
        from api.models.ladder import LadderAspect
        
        if event_type == "PAY_CHANGE":
            salary_change = parse_float_or_none(row.get("salary_change")) or 0.0
            if salary_change > 0:
                return f"افزایش پله‌ی حقوقی: {salary_change}"
            elif salary_change < 0:
                return f"کاهش پله‌ی حقوقی: {salary_change}"
            else:
                return "تغییر بسته حقوقی"
        
        elif event_type == "BONUS_PAYOUT":
            bonus_percentage = parse_float_or_none(row.get("bonus_percentage")) or 0.0
            if bonus_percentage > 0:
                return f"پرداخت پاداش - {bonus_percentage}٪ از حقوق"
            else:
                return "پرداخت پاداش"
        
        elif event_type == "MAPPING":
            ladder_code = (row.get("ladder_code") or "").strip()
            ladder_title = (row.get("ladder_title") or "").strip()
            overall_score = parse_float_or_none(row.get("overall_score"))
            details = parse_json_dict(row.get("aspect_details_json"))
            stages_raw = parse_json_dict(row.get("aspect_stages_json")) or {}
            
            if ladder_title:
                ladder_name = ladder_title
            elif ladder_code:
                ladder_name = ladder_code
            else:
                ladder_name = "نامشخص"
            
            # Get ladder and aspects for detailed description
            from api.models.ladder import Ladder
            ladder = Ladder.objects.filter(code=ladder_code).first() if ladder_code else None
            
            if ladder and details:
                # Get aspect names
                aspect_names = {}
                for aspect in LadderAspect.objects.filter(ladder=ladder):
                    aspect_names[aspect.code] = aspect.name
                
                # Build detailed mapping text like seniority changes
                aspect_details = []
                for code, level in details.items():
                    aspect_name = aspect_names.get(code, code)
                    stage_label = stages_raw.get(code)
                    stage_label_clean = stage_label.replace('\u200c', '') if stage_label else None
                    stage_text = f" - محدوده: {stage_label_clean}" if stage_label_clean else ""
                    
                    aspect_details.append(f"در بعد {aspect_name}، سطح: {level}{stage_text}")
                
                if aspect_details:
                    detailed_text = "\n".join(aspect_details)
                    if overall_score is not None:
                        detailed_text += f"\n\nسطح کلی: {overall_score}"
                    return f"مپ به لدر {ladder_name}\n{detailed_text}"
            
            # Fallback to simple description
            if overall_score is not None:
                return f"مپ به لدر {ladder_name} - سطح: {overall_score}"
            else:
                return f"مپ به لدر {ladder_name} - سطح: مشخص نشد."
        
        elif event_type == "SENIORITY_CHANGE":
            # Generate detailed seniority change description like signals.py
            ladder_code = (row.get("ladder_code") or "").strip()
            details = parse_json_dict(row.get("aspect_details_json"))
            stages_raw = parse_json_dict(row.get("aspect_stages_json")) or {}
            
            if not ladder_code or not details:
                return "تغییر سطح لدر"
            
            # Get ladder and aspects
            from api.models.ladder import Ladder
            ladder = Ladder.objects.filter(code=ladder_code).first()
            if not ladder:
                return "تغییر سطح لدر"
            
            # Get aspect names
            aspect_names = {}
            for aspect in LadderAspect.objects.filter(ladder=ladder):
                aspect_names[aspect.code] = aspect.name
            
            # Get previous snapshot for comparison (before the current event date)
            from api.models.performance_tables import SenioritySnapshot
            from datetime import datetime
            effective_date = parse_date(row.get("event_date"))
            
            # Get the most recent snapshot BEFORE the current event date
            latest_snapshot = SenioritySnapshot.objects.filter(
                user=user,
                ladder=ladder,
                effective_date__lt=effective_date
            ).order_by('effective_date', 'date_created').last()
            
            # Build seniority change text
            aspect_changes = []
            for code, new_level in details.items():
                aspect_name = aspect_names.get(code, code)
                old_level = latest_snapshot.details_json.get(code, 0) if latest_snapshot else 0
                change_amount = new_level - old_level
                
                stage_label = stages_raw.get(code)
                stage_label_clean = stage_label.replace('\u200c', '') if stage_label else None
                stage_text = f" - محدوده: {stage_label_clean}" if stage_label_clean else ""
                
                # Check if there's a stage change
                old_stage = latest_snapshot.stages_json.get(code) if latest_snapshot else None
                stage_changed = stage_label and stage_label != old_stage
                
                if change_amount == 0 and not stage_changed:
                    # No change at all
                    aspect_changes.append(f"در بعد {aspect_name}، بدون تغییر. سطح: {old_level}{stage_text}")
                elif change_amount == 0 and stage_changed:
                    # Only stage changed
                    def _short(label):
                        if not label:
                            return None
                        s = label.replace('\u200c', '').split()[0]
                        return s[:-1] if s.endswith('ی') else s
                    old_short = _short(old_stage) or 'نامشخص'
                    new_short = _short(stage_label_clean) or ''
                    new_phrase = stage_label_clean
                    aspect_changes.append(f"در بعد {aspect_name}، بدون تغییر. سطح: {old_level} - تغییر محدوده از {old_short} به {new_phrase}")
                elif change_amount > 0 and stage_changed:
                    # Both level and stage changed → use suffix form for stage
                    aspect_changes.append(f"در بعد {aspect_name}، ارتقا از سطح {old_level} به {new_level} (+{change_amount}) - محدوده: {stage_label}")
                else:
                    # Only level changed
                    # If stage present, append in short suffix form
                    if stage_label:
                        aspect_changes.append(f"در بعد {aspect_name}، ارتقا از سطح {old_level} به {new_level} (+{change_amount}) - محدوده: {stage_label}")
                    else:
                        aspect_changes.append(f"در بعد {aspect_name}، ارتقا از سطح {old_level} به {new_level} (+{change_amount})")
            
            if aspect_changes:
                # Calculate overall level change
                old_details = latest_snapshot.details_json if latest_snapshot else {}
                old_overall = 0
                if old_details:
                    old_overall = round(sum(old_details.values()) / len(old_details), 1)
                
                new_overall = round(sum(details.values()) / len(details), 1) if details else 0
                
                seniority_text = "\n".join(aspect_changes)
                if old_overall != new_overall:
                    seniority_text += f"\n\nسطح کلی: از {old_overall} به {new_overall}"
                
                return seniority_text
            else:
                return "تغییر سطح لدر"
        
        elif event_type == "EVALUATION":
            # Check if we have rich data to generate detailed summary
            perf_label = (row.get("performance_label") or "").strip()
            ladder_code = (row.get("ladder_code") or "").strip()
            ladder_title = (row.get("ladder_title") or "").strip()
            overall_score = parse_float_or_none(row.get("overall_score"))
            details = parse_json_dict(row.get("aspect_details_json"))
            
            # If we have rich data, use it to generate detailed summary
            if ladder_code or ladder_title or overall_score is not None or details:
                if ladder_title:
                    ladder_name = ladder_title
                elif ladder_code:
                    ladder_name = ladder_code
                else:
                    ladder_name = "نامشخص"
                
                from api.models.ladder import Ladder
                ladder = Ladder.objects.filter(code=ladder_code).first() if ladder_code else None
                
                if ladder and details:
                    from api.models.ladder import LadderAspect
                    aspect_names = {}
                    for aspect in LadderAspect.objects.filter(ladder=ladder):
                        aspect_names[aspect.code] = aspect.name
                    
                    aspect_details = []
                    for code, level in details.items():
                        aspect_name = aspect_names.get(code, code)
                        aspect_details.append(f"در بعد {aspect_name}، سطح: {level}")
                    
                    if aspect_details:
                        detailed_text = "\n".join(aspect_details)
                        if overall_score is not None:
                            detailed_text += f"\n\nسطح کلی: {overall_score}"
                        return f"ارزیابی عملکرد - {ladder_name}\n{detailed_text}"
                
                if overall_score is not None:
                    return f"ارزیابی عملکرد - {ladder_name} - سطح: {overall_score}"
                else:
                    return f"ارزیابی عملکرد - {ladder_name}"
            
            # If no rich data, use performance_label or fallback
            if perf_label:
                return perf_label
            else:
                return "ارزیابی عملکرد"
        
        elif event_type == "NOTICE":
            return "نوتیس عملکردی ثبت شد."
        
        elif event_type == "LADDER_CHANGED":
            # This would need old and new ladder names, which might not be in CSV
            return "تغییر لدر"
        
        else:
            # Fallback to original summary_text or generic message
            original_summary = (row.get("summary_text") or "").strip()
            if original_summary:
                return original_summary
            else:
                return "خروجی ایمپورت شده"


