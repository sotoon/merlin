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