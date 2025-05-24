from rest_framework import permissions

from api.models import NoteUserAccess, Cycle

 
class IsCurrentCycleEditable(permissions.BasePermission):
    """
    Only allow editing OneOnOne notes if their cycle is the current cycle.
    """
    message = "You can only edit One-on-Ones in the current cycle."

    def has_object_permission(self, request, view, obj):
        # Allow all safe (read-only) methods
        if request.method in permissions.SAFE_METHODS:
            return True
        current = Cycle.get_current_cycle()
        
        if current is None:
            self.message = "No active cycle exists; editing is disabled."
            return False
        return obj.cycle_id == current.id


                                                    # FUTURE ENHANCEMENT: Since a single NoteUserAccess row per (user, note) is guaranteed, use the logic on HasOneOnOnePermission: fetch once, use attr
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
                note=view.get_note(), user=request.user, can_view_summary=True
            ).exists()
        return NoteUserAccess.objects.filter(
            note=view.get_note(), user=request.user, can_write_summary=True
        ).exists()


class IsLeaderForMember(permissions.BasePermission):
    """
    Allow create (POST) on /my-team/<member_pk>/one-on-ones
    only if the authenticated user is the member's direct leader.
    """

    def has_permission(self, request, view):
        if view.action != "create":
            return True

        member_pk = view.kwargs.get("member_pk")
        from api.models import User
        try:
            member = User.objects.get(uuid=member_pk)
        except User.DoesNotExist:
            return False

        allowed = (
            request.user.id != member.id and          # not the member
            request.user.id == member.leader_id       # is the leader
        )

        return allowed


class HasOneOnOneAccess(permissions.BasePermission):
    """
    Object-level permission for One-on-One notes.
    Mirrors NotePermission's fine-grained logic.
    """
    def _get_access(self, request, obj):
        try:
            return NoteUserAccess.objects.get(user=request.user, note=obj.note)
        except NoteUserAccess.DoesNotExist:
            return None

    def has_object_permission(self, request, view, obj):
        access = self._get_access(request, obj)
                
        if access is None:
            return False

        if request.method in permissions.SAFE_METHODS:
            return access.can_view

        if request.method in ("PUT", "PATCH"):
            keys = set(request.data.keys())
            if keys == {"leader_vibe"}:
                return access.can_edit
            if keys == {"member_vibe"}:
                return access.can_write_feedback
            return access.can_edit

        return access.can_edit