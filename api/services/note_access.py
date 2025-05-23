# This file contains deferred imports

__all__ = ['ensure_leader_note_accesses', 'grant_oneonone_access', 'get_notes_visible_to']

def ensure_leader_note_accesses(self, new_leader):
    """
    Whenever a user's `leader` changes, grant the new leader the correct
    NoteUserAccess rows for all existing notes of that user.
    """
    from api.models import Note, NoteUserAccess, leader_permissions

    notes = Note.objects.filter(type__in=leader_permissions.keys(), owner=self)
    for note in notes:
        NoteUserAccess.ensure_note_predefined_accesses(note)


def get_notes_visible_to(user):
    """
    Returns all notes this user can view (of any type).
    """
    from api.models import Note, NoteUserAccess

    accessible_note_ids = NoteUserAccess.objects.filter(
        user=user, can_view=True
    ).values_list("note__uuid", flat=True)
    return Note.objects.filter(uuid__in=accessible_note_ids)

def grant_oneonone_access(note):
    """Create NoteUserAccess rows for leader (note.owner) and member only."""
    from api.models import NoteUserAccess, NoteType

    if note.type != NoteType.ONE_ON_ONE:
        return
    
    member = note.one_on_one.member

    if member is None or note.owner is None:
        return
        
    # leader / owner
    NoteUserAccess.objects.update_or_create(
        user=note.owner,
        note=note,
        # Update all the permission fields (not all fields as kwargs)
        defaults={      
            "can_view": True,  "can_edit": True,
            "can_view_summary": False,  "can_write_summary": False,
            "can_view_feedbacks": True, "can_write_feedback": True,
        },
    )

    # member
    NoteUserAccess.objects.update_or_create(
        user=member,
        note=note,
        defaults={
            "can_view": True,  "can_edit": False,
            "can_view_summary": False,  "can_write_summary": False,
            "can_view_feedbacks": True, "can_write_feedback": True,
        },
    )