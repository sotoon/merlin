from rest_framework import permissions

from api.models import Note, NoteType, User


def validate_read_note_permission(request, note):
    if note.owner == request.user:
        return True
    if note.type == NoteType.Personal:
        return False
    if note.owner.check_is_leader(request.user) and note.type != NoteType.Message:
        return True
    if note in Note.retrieve_mentions(request.user):
        return True
    return False


def validate_update_note_permission(request, note):
    is_updating_summary = "summary" in request.data
    is_updating_content = False
    for key in request.data.keys():
        if key != "summary":
            is_updating_content = True
    if is_updating_content:
        if is_updating_summary:
            return False
        return note.owner == request.user
    if is_updating_summary:
        return note.owner.check_is_leader(request.user)
    return False


class NotePermission(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        user_email = request.query_params.get("user")
        if user_email:
            notes_owner = User.objects.get(email=user_email)
            return notes_owner.check_is_leader(request.user)
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method == "POST":
            return super().has_object_permission(request, view, obj)
        if request.method in permissions.SAFE_METHODS:
            return validate_read_note_permission(request, obj)
        if request.method in ["PUT", "PATCH"]:
            return validate_update_note_permission(request, obj)
        return obj.owner == request.user


class FeedbackPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST":
            return validate_read_note_permission(request, view.get_note())
        return obj.note == view.get_note() and obj.owner == request.user
