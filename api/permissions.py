from rest_framework import permissions

from api.models import NoteUserAccess


class NotePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method == "POST":
            return super().has_object_permission(request, view, obj)
        if request.method in permissions.SAFE_METHODS:
            return NoteUserAccess.objects.filter(
                note=obj, user=request.user, can_view=True
            ).exists()
        if request.method in ["PUT", "PATCH"]:
            if "summary" in request.data:
                return NoteUserAccess.objects.filter(
                    note=obj, user=request.user, can_write_summary=True
                ).exists()
            return NoteUserAccess.objects.filter(
                note=obj, user=request.user, can_edit=True
            ).exists()
        return obj.owner == request.user


class FeedbackPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return NoteUserAccess.objects.filter(
                note=view.get_note(), user=request.user, can_view_feedbacks=True
            ).exists()
        return NoteUserAccess.objects.filter(
            note=view.get_note(), user=request.user, can_write_feedback=True
        ).exists()


class SummaryPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return NoteUserAccess.objects.filter(
                note=view.get_note(), user=request.user, can_view=True
            ).exists()
        return NoteUserAccess.objects.filter(
            note=view.get_note(), user=request.user, can_write_summary=True
        ).exists()
