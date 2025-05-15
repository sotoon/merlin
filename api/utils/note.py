from api.models.note import NoteUserAccess

def grant_oneonone_access(note):
    """Create NoteUserAccess rows for leader (note.owner) and member only."""
    member = note.one_on_one.member
    
    # Remove any default rows created via mentioned_users etc.
    NoteUserAccess.objects.filter(note=note).delete()

    # leader / owner
    NoteUserAccess.objects.create(
        user=note.owner,
        note=note,
        can_view=True,  can_edit=True,
        can_view_summary=False,  can_write_summary=False,
        can_view_feedbacks=True, can_write_feedback=True,
    )

    # member
    NoteUserAccess.objects.create(
        user=member,
        note=note,
        can_view=True,  can_edit=False,
        can_view_summary=False,  can_write_summary=False,
        can_view_feedbacks=True, can_write_feedback=True,
    )