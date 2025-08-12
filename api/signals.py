import re
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal

from .models import (
    Committee,
    Note,
    NoteType,
    NoteUserAccess,
    Summary,
    SummarySubmitStatus,
    NoteSubmitStatus,
    User,
    Form,
    FormAssignment,
    OneOnOne,
    ValueTag,
    ProposalType,
    Notice,
    LadderStage,
    LadderAspect,
    Team,
)

from api.models import OrgAssignmentSnapshot

from api.models.timeline import (
    TimelineEvent,
    EventType,
    StockGrant as StockGrantModel,
    TitleChange as TitleChangeModel,
    CompensationSnapshot,
    SenioritySnapshot,
    PayBand,
)
from api.serializers.note import get_current_user


# ────────────────────────────────────────────────────────────────
# Note access
# ----------------------------------------------------------------


@receiver(post_save, sender=Note)
def ensure_note_predefined_access(sender, instance, created, **kwargs):
    NoteUserAccess.ensure_note_predefined_accesses(instance)


@receiver(m2m_changed, sender=Committee.members.through)
def handle_committee_members_changed(sender, instance, action, pk_set, **kwargs):
    changed_users = User.objects.filter(committee=instance)
    for user in changed_users:
        notes = Note.objects.filter(type=NoteType.Proposal, owner=user)
        for note in notes:
            NoteUserAccess.ensure_note_predefined_accesses(note)


@receiver(m2m_changed, sender=Note.mentioned_users.through)
def handle_mentioned_users_changed(sender, instance, action, pk_set, **kwargs):
    NoteUserAccess.ensure_note_predefined_accesses(instance)


@receiver(m2m_changed, sender=Committee.roles.through)
def handle_committee_roles_changed(sender, instance, action, **kwargs):
    """Recompute ACLs for all users of a committee when its role list changes."""
    if action not in ("post_add", "post_remove", "post_clear"):
        return

    from api.models import NoteType, NoteSubmitStatus  # local import to avoid circular

    affected_users = instance.committee_users.all()
    for user in affected_users:
        notes = user.note_set.filter(type=NoteType.Proposal,
                                     submit_status__in=[NoteSubmitStatus.PENDING, NoteSubmitStatus.REVIEWED])
        for note in notes:
            NoteUserAccess.ensure_note_predefined_accesses(note)


@receiver(post_save, sender=Summary)
def ensure_summary_predefined_access(sender, instance, created, **kwargs):
    if instance.submit_status == SummarySubmitStatus.DONE:
        instance.note.submit_status = NoteSubmitStatus.REVIEWED
        instance.note.save()


# ────────────────────────────────────────────────────────────────
# Assessment form assignment
# ----------------------------------------------------------------

@receiver(post_save, sender=Form)
def assign_default_forms(sender, instance, created, **kwargs):
    """
    Automatically assign default forms to users when a form is marked default,
    and its cycle is active. Prevent duplicate assignments.
    """
    if not instance.is_default:  # Skip non-default forms
        return

    if instance.is_default and instance.cycle.is_active:
        users = User.objects.all()
        assignments = []
        affected_users = []
        skipped_users = []

        for user in users:
            # Check if the user is already assigned to this form
            if FormAssignment.objects.filter(form=instance, assigned_to=user).exists():
                skipped_users.append(user)
                continue

            assigned_by = None

            if instance.form_type == Form.FormType.TL:
                leaders = user.get_leaders()
                if not leaders:
                    skipped_users.append(user)
                    continue

                affected_users.append(user)

            elif instance.form_type == Form.FormType.PM:
                # PM forms require manual assignment for now            FUTURE ENHANCEMENT: dynamic assignment for PMs
                skipped_users.append(user)
                continue

            else:
                skipped_users.append(user)
                assigned_by = None

        # Run the query only for affected_users
        assignments = [
            FormAssignment(
                form=instance,
                assigned_to=user,
                assigned_by=user.get_leaders()[0] if user.get_leaders() else None,
                deadline=instance.cycle.end_date
            )
            for user in affected_users
        ]

        FormAssignment.objects.bulk_create(assignments)


# This is for future-proofing DB integrity
@receiver(m2m_changed, sender=OneOnOne.tags.through)
def prevent_disabled_tags(sender, instance, action, pk_set, **kwargs):
    if action == "pre_add":
        bad_tags = ValueTag.objects.filter(pk__in=pk_set, orgvaluetag__is_enabled=False)
        if bad_tags.exists():
            raise Exception("Cannot add disabled tags to OneOnOne.")


# ────────────────────────────────────────────────────────────────
# Helper to create timeline event
# ----------------------------------------------------------------

def _create_timeline_event(*, user, event_type, summary_text, effective_date, source_obj=None, created_by=None):
    content_type = None
    object_id = None
    if source_obj is not None:
        content_type = ContentType.objects.get_for_model(source_obj.__class__)
        object_id = source_obj.pk

    TimelineEvent.objects.create(
        user=user,
        event_type=event_type,
        summary_text=summary_text,
        effective_date=effective_date,
        content_type=content_type,
        object_id=object_id,
        created_by=created_by,
        visibility_mask=1,  # TODO: Compute proper visibility_mask
    )


# ────────────────────────────────────────────────────────────────
# Summary finalised + EVALUATION event + snapshots
# ----------------------------------------------------------------


@receiver(post_save, sender=Summary)
def summary_to_timeline(sender, instance: Summary, created, update_fields, **kwargs):
    if instance.submit_status != SummarySubmitStatus.DONE:
        return

    # Check if an event already exists to avoid duplicates
    if TimelineEvent.objects.filter(content_type__model="summary", object_id=instance.pk).exists():
        return

    effective_date = instance.committee_date or instance.date_created.date()

    # Check for ladder change FIRST and create timeline event
    # Get the latest snapshot for this user to check if ladder changed
    latest_snapshot = SenioritySnapshot.objects.filter(
        user=instance.note.owner
    ).order_by('effective_date', 'date_created').last()
    
    # Debug: Print ladder change detection info
    print(f"DEBUG: Latest snapshot ladder: {latest_snapshot.ladder.name if latest_snapshot else 'None'}")
    print(f"DEBUG: Summary ladder: {instance.ladder.name if instance.ladder else 'None'}")
    print(f"DEBUG: Ladder changed: {latest_snapshot.ladder != instance.ladder if latest_snapshot and instance.ladder else 'No comparison'}")
    
    if latest_snapshot and instance.ladder and latest_snapshot.ladder != instance.ladder:
        # Ladder has changed, create LADDER_CHANGED event FIRST
        old_ladder_name = latest_snapshot.ladder.name
        new_ladder_name = instance.ladder.name
        ladder_change_text = f"لدر کاربر از {old_ladder_name} به {new_ladder_name} تغییر کرد."
        
        print(f"DEBUG: Creating LADDER_CHANGED event: {ladder_change_text}")
        _create_timeline_event(
            user=instance.note.owner,
            event_type=EventType.LADDER_CHANGED,
            summary_text=ladder_change_text,
            effective_date=effective_date,
            source_obj=instance,
            created_by=get_current_user(),
        )

    # Determine proposal type
    ptype = getattr(instance.note, "proposal_type", ProposalType.PROMOTION)
    
    # Generate timeline events based on proposal type
    if ptype in [ProposalType.PROMOTION, ProposalType.EVALUATION]:
        _create_promotion_evaluation_events(instance, effective_date)
    elif ptype == ProposalType.NOTICE:
        _create_notice_event(instance, effective_date)
    elif ptype == ProposalType.MAPPING:
        _create_mapping_event(instance, effective_date)

    # Create snapshots if needed
    if instance.salary_change or instance.bonus or instance.ladder_change or (instance.ladder and instance.aspect_changes):
        # Compensation snapshot: compute new pay band from latest pay band + salary_change (supports 0.5)
        if instance.salary_change or instance.bonus:
            # Validate increment granularity
            if instance.salary_change and round(instance.salary_change * 2) != instance.salary_change * 2:
                # Non 0.5 step – ignore or round; choose to round to nearest .5 to avoid crash
                instance.salary_change = round(instance.salary_change * 2) / 2.0

            # Find latest compensation snapshot for baseline pay band
            latest_comp = CompensationSnapshot.objects.filter(user=instance.note.owner).order_by("-effective_date", "-date_created").first()
            current_band = getattr(latest_comp, "pay_band", None)

            new_band = current_band
            if current_band is not None and instance.salary_change:
                # Create or get a PayBand with incremented number
                target_number = float(current_band.number) + float(instance.salary_change)
                # Enforce 0.5 rounding
                target_number = round(target_number * 2) / 2.0
                new_band, _ = PayBand.objects.get_or_create(number=target_number)

            CompensationSnapshot.objects.create(
                user=instance.note.owner,
                pay_band=new_band or current_band,
                salary_change=float(instance.salary_change or 0.0),
                bonus_percentage=instance.bonus or 0,
                effective_date=effective_date,
            )
        # Persist new seniority snapshot when ladder & aspect changes present
        if instance.ladder and instance.aspect_changes:
            # Extract changed aspects from the summary
            deltas = {
                code: data.get("new_level")
                for code, data in instance.aspect_changes.items()
                if data.get("changed") and data.get("new_level") is not None
            }
            stages = {
                code: data.get("stage")
                for code, data in instance.aspect_changes.items()
                if data.get("changed") and data.get("stage") is not None
            }

            from django.db import transaction

            with transaction.atomic():
                # Get the latest snapshot for this user and ladder
                latest_snapshot = SenioritySnapshot.objects.filter(
                    user=instance.note.owner,
                    ladder=instance.ladder
                ).order_by('effective_date', 'date_created').last()
                # Compute overall score and persist snapshot
                _persist_seniority_snapshot(instance, latest_snapshot, deltas, stages, effective_date)


def _create_promotion_evaluation_events(instance: Summary, effective_date):
    """Create timeline events for PROMOTION and EVALUATION proposals."""
    events_created = []
    
    # Get the member (note owner) instead of the leader
    member = instance.note.owner
    
    # Get the current user who created the summary
    created_by_user = get_current_user()
    
    # Salary change event
    if instance.salary_change and instance.salary_change > 0:
        _create_timeline_event(
            user=member,
            event_type=EventType.PAY_CHANGE,
            summary_text=f"افزایش پله‌ی حقوقی: {instance.salary_change}",
            effective_date=effective_date,
            source_obj=instance,
            created_by=created_by_user,
        )
        events_created.append(EventType.PAY_CHANGE)
    
    # Seniority change event (if there are aspect changes)
    if instance.ladder and instance.aspect_changes:
        # Get aspect names
        aspect_names = {}
        for aspect in LadderAspect.objects.filter(ladder=instance.ladder):
            aspect_names[aspect.code] = aspect.name
        
        # Get previous snapshot for comparison
        latest_snapshot = SenioritySnapshot.objects.filter(
            user=member,
            ladder=instance.ladder
        ).order_by('effective_date', 'date_created').last()
        
        # Build seniority change text
        aspect_changes = []
        for code, data in instance.aspect_changes.items():
            if data.get("changed"):
                aspect_name = aspect_names.get(code, code)
                old_level = latest_snapshot.details_json.get(code, 0) if latest_snapshot else 0
                change_amount = data.get("new_level", 0)
                new_level = old_level + change_amount  # Add to existing level
                
                stage_label = data.get('stage')
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
                    # Convert stages to desired short/long forms
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
            # Calculate overall level change using ALL aspects of the ladder
            # Get all aspects for this ladder
            all_aspects = LadderAspect.objects.filter(ladder=instance.ladder)
            
            # Calculate old overall using all aspects
            old_details = latest_snapshot.details_json if latest_snapshot else {}
            old_overall = 0
            if old_details:
                old_overall = round(sum(old_details.values()) / len(old_details), 1)
            
            # Calculate new overall using all aspects
            new_details = {}
            for aspect in all_aspects:
                # Add new_level to existing level if aspect was changed, otherwise use old level
                if aspect.code in instance.aspect_changes and instance.aspect_changes[aspect.code].get("changed"):
                    old_level = old_details.get(aspect.code, 0)
                    change_amount = instance.aspect_changes[aspect.code].get("new_level", 0)
                    new_details[aspect.code] = old_level + change_amount
                else:
                    new_details[aspect.code] = old_details.get(aspect.code, 0)
            
            new_overall = round(sum(new_details.values()) / len(new_details), 1) if new_details else 0
            
            seniority_text = "\n".join(aspect_changes)
            if old_overall != new_overall:
                seniority_text += f"\n\nسطح کلی: از {old_overall} به {new_overall}"
            
            _create_timeline_event(
                user=member,
                event_type=EventType.SENIORITY_CHANGE,
                summary_text=seniority_text,
                effective_date=effective_date,
                source_obj=instance,
                created_by=created_by_user,
            )
            events_created.append(EventType.SENIORITY_CHANGE)
    else:
        pass # No ladder or aspect_changes
    
    # Bonus event
    if instance.bonus and instance.bonus > 0:
        _create_timeline_event(
            user=member,
            event_type=EventType.BONUS_PAYOUT,
            summary_text=f"پرداخت پاداش - {instance.bonus}٪ از حقوق",
            effective_date=effective_date,
            source_obj=instance,
            created_by=created_by_user,
        )
        events_created.append(EventType.BONUS_PAYOUT)
    
    # Always create EVALUATION event for EVALUATION proposals
    if instance.note.proposal_type == ProposalType.EVALUATION:
        _create_timeline_event(
            user=member,
            event_type=EventType.EVALUATION,
            summary_text=instance.performance_label or "ارزیابی عملکرد",
            effective_date=effective_date,
            source_obj=instance,
            created_by=created_by_user,
        )
    # For PROMOTION proposals, create a general evaluation event only if no other events were created
    elif not events_created:
        _create_timeline_event(
            user=member,
            event_type=EventType.EVALUATION,
            summary_text=instance.performance_label or "خروجی کمیته",
            effective_date=effective_date,
            source_obj=instance,
            created_by=created_by_user,
        )


def _create_notice_event(instance: Summary, effective_date):
    """Create timeline event for NOTICE proposals."""
    # Get the member (note owner) instead of the leader
    member = instance.note.owner
    
    # Get the current user who created the summary
    created_by_user = get_current_user()
    
    # Use static text for notice events
    notice_text = "نوتیس عملکردی ثبت شد."
    
    _create_timeline_event(
        user=member,
        event_type=EventType.NOTICE,
        summary_text=notice_text,
        effective_date=effective_date,
        source_obj=instance,
        created_by=created_by_user,
    )


def _create_mapping_event(instance: Summary, effective_date):
    """Create timeline event for MAPPING proposals."""
    # Get the member (note owner) instead of the leader
    member = instance.note.owner
    
    # Get the current user who created the summary
    created_by_user = get_current_user()
    
    # Salary change event for MAPPING proposals
    if instance.salary_change and instance.salary_change > 0:
        _create_timeline_event(
            user=member,
            event_type=EventType.PAY_CHANGE,
            summary_text=f"افزایش پله‌ی حقوقی: {instance.salary_change}",
            effective_date=effective_date,
            source_obj=instance,
            created_by=created_by_user,
        )
    
    if instance.ladder and instance.aspect_changes:
        # Calculate overall level the same way as snapshot creation
        # Get all aspects for this ladder
        aspects = LadderAspect.objects.filter(ladder=instance.ladder)
        
        # Build the complete details dictionary with all aspects
        details = {}
        for aspect in aspects:
            # Use new_level if aspect was changed, otherwise use default 0
            new_level = instance.aspect_changes.get(aspect.code, {}).get("new_level", 0)
            details[aspect.code] = new_level
        
        # Calculate overall level using ALL aspects (same as snapshot creation)
        overall_level = round(sum(details.values()) / len(details), 1) if details else 0
        
        mapping_text = f"مپ به لدر {instance.ladder.name if instance.ladder else 'نامشخص'} - سطح: {overall_level}"
    else:
        mapping_text = "مپ به لدر - سطح: مشخص نشد."
    
    _create_timeline_event(
        user=member,
        event_type=EventType.MAPPING,
        summary_text=mapping_text,
        effective_date=effective_date,
        source_obj=instance,
        created_by=created_by_user,
                )


# ────────────────────────────────────────────────────────────────
# Lightweight artefacts → timeline events
# ----------------------------------------------------------------


@receiver(post_save, sender=Notice)
def notice_to_timeline(sender, instance: Notice, created, **kwargs):
    if not created:
        return
    _create_timeline_event(
        user=instance.user,
        event_type=EventType.NOTICE,
        summary_text=f"نوتیس {instance.get_notice_type_display()}",
        effective_date=instance.committee_date,
        source_obj=instance,
        created_by=instance.created_by,
    )


@receiver(post_save, sender=StockGrantModel)
def stockgrant_to_timeline(sender, instance: StockGrantModel, created, **kwargs):
    if not created:
        return
    _create_timeline_event(
        user=instance.user,
        event_type=EventType.STOCK_GRANT,
        summary_text=instance.description or "تخصیص سهام",
        effective_date=timezone.now().date(),
        source_obj=instance,
        created_by=instance.created_by,
    )


@receiver(post_save, sender=TitleChangeModel)
def titlechange_to_timeline(sender, instance: TitleChangeModel, created, **kwargs):
    if not created:
        return
    _create_timeline_event(
        user=instance.user,
        event_type=EventType.TITLE_CHANGE,
        summary_text=f"{instance.old_title} → {instance.new_title}",
        effective_date=instance.effective_date,
        source_obj=instance,
        created_by=instance.created_by,
    )


def _persist_seniority_snapshot(instance: Summary, latest_snapshot, deltas, stages, effective_date):
    """Persist a new SenioritySnapshot merging changes with previous snapshot and compute overall.
    This assumes deltas contains per-aspect additive level changes and stages contains stage updates.
    """
    # Start with existing details or create default for all aspects
    if latest_snapshot:
        details = latest_snapshot.details_json.copy()
        stages_json = (latest_snapshot.stages_json or {}).copy()
    else:
        # If no existing snapshot, create default for all aspects
        aspects = LadderAspect.objects.filter(ladder=instance.ladder)
        details = {aspect.code: 0 for aspect in aspects}  # Default level 0
        stages_json = {aspect.code: LadderStage.default() for aspect in aspects}

    # Add new changes to existing levels (not replace)
    for code, new_level in deltas.items():
        if code in details:
            details[code] += new_level  # Add to existing level
        else:
            details[code] = new_level  # Set new level if aspect didn't exist before

    # Update stages if provided
    for code, stage in stages.items():
        stages_json[code] = stage

    # Calculate overall score
    overall = round(sum(details.values()) / len(details), 1) if details else 0

    # Create new snapshot (don't update existing one for same date)
    SenioritySnapshot.objects.create(
        user=instance.note.owner,
        ladder=instance.ladder,
        effective_date=effective_date,
        details_json=details,
        stages_json=stages_json,
        overall_score=overall,
        title=instance.performance_label if getattr(instance, "performance_label", None) else "",
    )


@receiver(pre_save, sender=User)
def capture_org_assignment_on_user_change(sender, instance: User, **kwargs):
    """Create an OrgAssignmentSnapshot if a User's org fields change."""
    if not instance.pk:
        return
    try:
        prev = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        return

    org_fields_changed = any(
        getattr(prev, fname) != getattr(instance, fname)
        for fname in ("leader", "team", "chapter", "department")
    )
    if not org_fields_changed:
        return

    effective_date = timezone.now().date()
    OrgAssignmentSnapshot.objects.create(
        user=instance,
        leader=instance.leader,
        team=instance.team,
        tribe=getattr(instance.team, "tribe", None),
        chapter=instance.chapter,
        department=instance.department,
        effective_date=effective_date,
    )


@receiver(pre_save, sender=Team)
def capture_org_assignment_on_team_tribe_change(sender, instance: Team, **kwargs):
    """Create OrgAssignmentSnapshots for all team members if the team's tribe changes."""
    if not instance.pk:
        return
    try:
        prev = Team.objects.get(pk=instance.pk)
    except Team.DoesNotExist:
        return

    if prev.tribe_id == instance.tribe_id:
        return

    effective_date = timezone.now().date()
    members = User.objects.filter(team=instance)
    snapshots = [
        OrgAssignmentSnapshot(
            user=m,
            leader=m.leader,
            team=instance,
            tribe=instance.tribe,
            chapter=m.chapter,
            department=m.department,
            effective_date=effective_date,
        )
        for m in members
    ]
    if snapshots:
        OrgAssignmentSnapshot.objects.bulk_create(snapshots)