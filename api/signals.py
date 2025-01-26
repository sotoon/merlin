from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import (
    Committee,
    Note,
    NoteType,
    NoteUserAccess,
    User,
    Form,
    FormAssignment,)


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

@receiver(post_save, sender=Form)
def assign_default_forms(sender, instance, created, **kwargs):
    """
    Automatically assign default forms to users when a form is marked default,
    and its cycle is active.
    """
    if instance.is_default and instance.cycle.is_active:
        users = User.objects.all()
        assignments = []

        for user in users:
            if instance.form_type == Form.FormType.TL and not user.get_leaders():
                print(f"Warning: Skipping user {user.email}, no leader assigned.")
                continue

            assigned_by = user.get_leaders() if instance.form_type == Form.FormType.TL else None
            
            assignment = FormAssignment(
                    form=instance,
                    assigned_to=user,
                    assigned_by=assigned_by,
                    deadline=instance.cycle.end_date
                )
            assignments.append(assignment)

        FormAssignment.objects.bulk_create(assignments)
