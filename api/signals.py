from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Committee, Note, NoteType, NoteUserAccess, User, Summary, SummarySubmitStatus, NoteSubmitStatus


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

@receiver(post_save, sender=Summary)
def ensure_summary_predefined_access(sender, instance, created, **kwargs):
    if instance.submit_status == SummarySubmitStatus.DONE:
        instance.note.submit_status = NoteSubmitStatus.REVIEWED
        instance.note.save()
