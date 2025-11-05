# This file contains deferred imports

__all__ = [
    'ensure_leader_note_accesses',
    'grant_oneonone_access',
    'grant_feedback_access',
    'grant_feedback_request_access',
    'get_notes_visible_to'
]

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


def grant_feedback_access(note, receiver, mentioned_users=None, feedback_request=None):
    """
    Grant access to a Feedback note for sender, receiver, and mentioned users.
    
    This function ensures that feedback notes maintain privacy by granting access only to:
    - The sender (note owner)
    - The receiver
    - For ad-hoc feedback: Users explicitly mentioned in the feedback
    - For request answers: Users mentioned in the ORIGINAL REQUEST (not the answer)
    
    Leaders, agile coaches, and committee members are explicitly excluded from access.
    
    Args:
        note: The Note instance with type=FEEDBACK
        receiver: The User who receives the feedback
        mentioned_users: Optional list/queryset of Users mentioned in THIS answer (ignored for request answers)
        feedback_request: Optional FeedbackRequest instance if this is an answer to a request
    """
    from api.models import NoteUserAccess, NoteType

    if note.type != NoteType.FEEDBACK:
        return
    
    sender = note.owner

    if sender is None or receiver is None:
        return
    
    # Sender (owner) access
    NoteUserAccess.objects.update_or_create(
        user=sender,
        note=note,
        defaults={
            "can_view": True,
            "can_edit": True,
            "can_view_summary": False,
            "can_write_summary": False,
            "can_view_feedbacks": True,
            "can_write_feedback": True,
        },
    )
    
    # Receiver access
    NoteUserAccess.objects.update_or_create(
        user=receiver,
        note=note,
        defaults={
            "can_view": True,
            "can_edit": False,
            "can_view_summary": False,
            "can_write_summary": False,
            "can_view_feedbacks": True,
            "can_write_feedback": True,
        },
    )
    
    # Handle mentioned users based on feedback type
    if feedback_request:
        # For REQUEST ANSWERS: Grant access to users mentioned in the ORIGINAL REQUEST
        # This allows stakeholders mentioned in the request to see all answers
        request_note = feedback_request.note
        for mentioned_in_request in request_note.mentioned_users.all():
            NoteUserAccess.objects.update_or_create(
                user=mentioned_in_request,
                note=note,
                defaults={
                    "can_view": True,
                    "can_edit": False,
                    "can_view_summary": False,
                    "can_write_summary": False,
                    "can_view_feedbacks": True,
                    "can_write_feedback": False,  # They can only write if they're requestees
                },
            )
        # Note: Users mentioned in the ANSWER itself do NOT get access (privacy rule)
    else:
        # For AD-HOC FEEDBACK: Grant access to users mentioned in the answer itself
        if mentioned_users:
            for mentioned_user in mentioned_users:
                NoteUserAccess.objects.update_or_create(
                    user=mentioned_user,
                    note=note,
                    defaults={
                        "can_view": True,
                        "can_edit": False,
                        "can_view_summary": False,
                        "can_write_summary": False,
                        "can_view_feedbacks": True,
                        "can_write_feedback": True,
                    },
                )


def grant_feedback_request_access(note, requestees, mentioned_users=None):
    """
    Grant access to a FeedbackRequest note for owner, requestees, and mentioned users.
    
    This function ensures that feedback request notes are accessible to:
    - The owner (request creator)
    - All invited requestees
    - Any users explicitly mentioned in the request
    
    Args:
        note: The Note instance with type=FEEDBACK_REQUEST
        requestees: List/queryset of Users invited to respond to the request
        mentioned_users: Optional list/queryset of Users mentioned in the request
    """
    from api.models import NoteUserAccess, NoteType

    if note.type != NoteType.FEEDBACK_REQUEST:
        return
    
    owner = note.owner

    if owner is None:
        return
    
    # Owner access
    NoteUserAccess.objects.update_or_create(
        user=owner,
        note=note,
        defaults={
            "can_view": True,
            "can_edit": True,
            "can_view_summary": False,
            "can_write_summary": False,
            "can_view_feedbacks": True,
            "can_write_feedback": True,
        },
    )
    
    # Requestees access
    for requestee in requestees:
        NoteUserAccess.objects.update_or_create(
            user=requestee,
            note=note,
            defaults={
                "can_view": True,
                "can_edit": False,
                "can_view_summary": False,
                "can_write_summary": False,
                "can_view_feedbacks": False,
                "can_write_feedback": True,
            },
        )
    
    # Mentioned users access
    if mentioned_users:
        for mentioned_user in mentioned_users:
            NoteUserAccess.objects.update_or_create(
                user=mentioned_user,
                note=note,
                defaults={
                    "can_view": True,
                    "can_edit": False,
                    "can_view_summary": False,
                    "can_write_summary": False,
                    "can_view_feedbacks": False,
                    "can_write_feedback": True,
                },
            )