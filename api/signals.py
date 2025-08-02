import re
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone

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
)

from api.models.timeline import (
    TimelineEvent,
    EventType,
    StockGrant as StockGrantModel,
    TitleChange as TitleChangeModel,
    CompensationSnapshot,
    SenioritySnapshot,
    PayBand,
)
from api.models.ladder import Ladder
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
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(source_obj.__class__)
        object_id = source_obj.pk

    TimelineEvent.objects.create(
        user=user,
        event_type=event_type,
        summary_text=summary_text[:256],
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
        # PayBand lookup is out of scope; we still record salary change absolute value
        if instance.salary_change or instance.bonus:
            CompensationSnapshot.objects.create(
                user=instance.note.owner,
                pay_band=PayBand.objects.first() if PayBand.objects.exists() else None,
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

            from django.db import transaction

            with transaction.atomic():
                # Get the latest snapshot for this user and ladder
                latest_snapshot = SenioritySnapshot.objects.filter(
                    user=instance.note.owner,
                    ladder=instance.ladder
                ).order_by('effective_date').last()
                
                # Start with existing details or create default for all aspects
                if latest_snapshot:
                    details = latest_snapshot.details_json.copy()
                else:
                    # If no existing snapshot, create default for all aspects
                    from api.models import LadderAspect
                    aspects = LadderAspect.objects.filter(ladder=instance.ladder)
                    details = {aspect.code: 0 for aspect in aspects}  # Default level 0
                
                # Merge new changes
                details.update(deltas)
                
                # Calculate overall score
                overall = round(sum(details.values()) / len(details), 1) if details else 0
                
                # Create or update snapshot
                snapshot, created = SenioritySnapshot.objects.update_or_create(
                    user=instance.note.owner,
                    ladder=instance.ladder,
                    effective_date=effective_date,
                    defaults={
                        'details_json': details,
                        'overall_score': overall,
                        'title': instance.performance_label if instance.performance_label else ''
                    }
                )


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
        from api.models import LadderAspect
        aspect_names = {}
        for aspect in LadderAspect.objects.filter(ladder=instance.ladder):
            aspect_names[aspect.code] = aspect.name
        
        # Get previous snapshot for comparison
        latest_snapshot = SenioritySnapshot.objects.filter(
            user=member,
            ladder=instance.ladder
        ).order_by('effective_date').last()
        
        # Build seniority change text
        aspect_changes = []
        for code, data in instance.aspect_changes.items():
            if data.get("changed") and data.get("new_level"):
                aspect_name = aspect_names.get(code, code)
                old_level = latest_snapshot.details_json.get(code, 1) if latest_snapshot else 1
                new_level = data.get("new_level")
                
                if old_level == new_level:
                    aspect_changes.append(f"در بعد {aspect_name}، بدون تغییر. سطح: {new_level}")
                else:
                    aspect_changes.append(f"در بعد {aspect_name}، ارتقا از سطح {old_level} به {new_level}")
        
        if aspect_changes:
            # Calculate overall level change using ALL aspects of the ladder
            # Get all aspects for this ladder
            from api.models import LadderAspect
            all_aspects = LadderAspect.objects.filter(ladder=instance.ladder)
            
            # Calculate old overall using all aspects
            old_details = latest_snapshot.details_json if latest_snapshot else {}
            old_overall = 0
            if old_details:
                old_overall = round(sum(old_details.values()) / len(old_details), 1)
            
            # Calculate new overall using all aspects
            new_details = {}
            for aspect in all_aspects:
                # Use new_level if aspect was changed, otherwise use old level
                if aspect.code in instance.aspect_changes and instance.aspect_changes[aspect.code].get("changed"):
                    new_details[aspect.code] = instance.aspect_changes[aspect.code].get("new_level", old_details.get(aspect.code, 0))
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
    
    # For now, use the content as notice description
    # In the future, this should be linked to the Notice model
    notice_text = instance.content or "نوتیس"
    # Clean HTML tags
    notice_text = re.sub(r'<[^>]+>', '', notice_text)
    
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
    
    if instance.ladder and instance.aspect_changes:
        # Calculate overall level the same way as snapshot creation
        # Get all aspects for this ladder
        from api.models import LadderAspect
        aspects = LadderAspect.objects.filter(ladder=instance.ladder)
        
        # Build the complete details dictionary with all aspects
        details = {}
        for aspect in aspects:
            # Use new_level if aspect was changed, otherwise use default 0
            new_level = instance.aspect_changes.get(aspect.code, {}).get("new_level", 0)
            details[aspect.code] = new_level
        
        # Calculate overall level using ALL aspects (same as snapshot creation)
        overall_level = round(sum(details.values()) / len(details), 1) if details else 0
        
        mapping_text = f"مپ به لدر {instance.ladder.name} - سطح: {overall_level}"
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