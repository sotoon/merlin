from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

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

    # Determine committee type
    committee = getattr(instance.note.owner, "committee", None)
    from api.models.organization import CommitteeType  # local import to avoid circular

    ctype = getattr(committee, "committee_type", CommitteeType.EVALUATION) if committee else CommitteeType.EVALUATION
    event_map = {
        CommitteeType.EVALUATION: EventType.EVALUATION,
        # Promotions may cause changes in Pay Band and/or Seniority.
        CommitteeType.PROMOTION: (
            (EventType.SENIORITY_CHANGE, EventType.PAY_CHANGE)
            if getattr(instance, "ladder_change", None) and getattr(instance, "salary_change", None)
            else EventType.SENIORITY_CHANGE
            if getattr(instance, "ladder_change", None)
            else EventType.PAY_CHANGE
            if getattr(instance, "salary_change", None)
            else EventType.SENIORITY_CHANGE  # fallback to seniority change if neither is set
        ),
        CommitteeType.MAPPING: EventType.MAPPING,
        CommitteeType.NOTICE: EventType.NOTICE,
    }
    event_type_value = event_map.get(ctype, EventType.EVALUATION)

    def _build_text(ev):
        if ev == EventType.EVALUATION:
            return (
                f"Committee result – Ladder {instance.ladder_change or '-'} / "
                f"Bonus {instance.bonus}% / Pay band ↑"
            )
        return instance.performance_label or "Committee outcome"

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
    if instance.salary_change or instance.bonus or instance.ladder_change:
        # PayBand lookup is out of scope; we still record salary change absolute value
        CompensationSnapshot.objects.create(
            user=instance.note.owner,
            pay_band=PayBand.objects.first() if PayBand.objects.exists() else None,
            bonus_percentage=instance.bonus or 0,
            effective_date=effective_date,
        )
        if instance.ladder_change:
            SenioritySnapshot.objects.create(
                user=instance.note.owner,
                ladder=Ladder.objects.filter(code=instance.ladder_change).first(),
                title="",
                overall_score=0,  # TODO compute from ladder steps
                details_json={},
                effective_date=effective_date,
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
        summary_text=f"{instance.get_notice_type_display()} notice",
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
        summary_text=f"{instance.shares} {instance.get_grant_type_display()} granted",
        effective_date=instance.cliff_date,
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