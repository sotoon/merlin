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
    ProposalType
)

from api.models.timeline import (
    TimelineEvent,
    EventType,
    Notice as NoticeModel,
    StockGrant as StockGrantModel,
    TitleChange as TitleChangeModel,
    CompensationSnapshot,
    SenioritySnapshot,
    PayBand,
)
from api.models.ladder import Ladder


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

    # Determine proposal type (falls back to PROMOTION)
    ptype = getattr(instance.note, "proposal_type", ProposalType.PROMOTION)
    event_map = {
        ProposalType.EVALUATION: EventType.EVALUATION,
        # Promotions may cause changes in Pay Band and/or Seniority.
        ProposalType.PROMOTION: (
            (EventType.SENIORITY_CHANGE, EventType.PAY_CHANGE)
            if getattr(instance, "ladder_change", None) and getattr(instance, "salary_change", None)
            else EventType.SENIORITY_CHANGE
            if getattr(instance, "ladder_change", None)
            else EventType.PAY_CHANGE
            if getattr(instance, "salary_change", None)
            else EventType.SENIORITY_CHANGE
        ),
        ProposalType.MAPPING: EventType.MAPPING,
        ProposalType.NOTICE: EventType.NOTICE,
    }
    event_type_value = event_map.get(ptype, EventType.EVALUATION)

    def _build_text(ev):
        if ev == EventType.EVALUATION:
            ladder = instance.ladder_change if instance.ladder_change else "-"
            bonus = f"{instance.bonus}%" if instance.bonus is not None else "۰٪"
            salary = (
                f"{instance.salary_change}%" if instance.salary_change else "۰٪"
            )
            return (
                f"نتیجه کمیته – لدر {ladder} / پاداش {bonus} / افزایش حقوق {salary}"
            )
        # For PAY_CHANGE / SENIORITY_CHANGE etc we fall back to performance_label if set.
        return instance.performance_label or "خروجی کمیته"

    # Handle promotions that generate two separate events
    if isinstance(event_type_value, tuple):
        for ev in event_type_value:
            _create_timeline_event(
                user=instance.note.owner,
                event_type=ev,
                summary_text=_build_text(ev)[:256],
                effective_date=effective_date,
                source_obj=instance,
                created_by=instance.note.owner,
            )
    else:
        _create_timeline_event(
            user=instance.note.owner,
            event_type=event_type_value,
            summary_text=_build_text(event_type_value)[:256],
            effective_date=effective_date,
            source_obj=instance,
            created_by=instance.note.owner,
        )

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
                    details = {aspect.code: 3 for aspect in aspects}  # Default level 3
                
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


# ────────────────────────────────────────────────────────────────
# Lightweight artefacts → timeline events
# ----------------------------------------------------------------


@receiver(post_save, sender=NoticeModel)
def notice_to_timeline(sender, instance: NoticeModel, created, **kwargs):
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