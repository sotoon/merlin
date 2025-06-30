from rest_framework import viewsets, permissions
from api.serializers.feedback import (
    FeedbackFormSerializer,
    FeedbackRequestReadOnlySerializer,
    FeedbackRequestWriteSerializer,
    FeedbackSerializer,
)
from api.models.note import FeedbackForm, FeedbackRequest, Feedback
from django.db.models import Q
from api.permissions import FeedbackEntryPermission, FeedbackRequestPermission
from rest_framework.decorators import action
from rest_framework.response import Response


class FeedbackFormViewSet(viewsets.ReadOnlyModelViewSet):
    """Publicly list active feedback forms."""

    queryset = FeedbackForm.objects.filter(is_active=True)
    serializer_class = FeedbackFormSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedbackRequestViewSet(viewsets.ModelViewSet):
    """
    Feedback-request CRUD.

    List endpoints are split:

        • /feedback-requests/owned/    requests user created
        • /feedback-requests/invited/  requests user should answer
    """
    queryset = FeedbackRequest.objects.all()
    permission_classes = [FeedbackRequestPermission]
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action in ["list_owned", "list_invited", "retrieve"]:
            return FeedbackRequestReadOnlySerializer
        return FeedbackRequestWriteSerializer

    # private helpers
    def _owned_qs(self):
        user = self.request.user
        return (
            self.queryset
            .filter(note__owner=user)
            .select_related("note", "note__owner")
            .prefetch_related("requestees__user")
        )

    def _invited_qs(self):
        user = self.request.user
        return (
            self.queryset
            .filter(requestees__user=user)
            .exclude(note__owner=user)
            .select_related("note", "note__owner")
            .prefetch_related("requestees__user")
        )

    # list endpoints
    @action(detail=False, methods=["get"], url_path="owned",   url_name="owned")
    def list_owned(self, request):
        """Return only the feedback-requests created by the current user."""
        serializer = self.get_serializer(self._owned_qs(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="invited", url_name="invited")
    def list_invited(self, request):
        """Return feedback-requests where the user was invited to give feedback."""
        serializer = self.get_serializer(self._invited_qs(), many=True)
        return Response(serializer.data)

    # list answers for one request
    @action(detail=True, methods=["get"], url_path="entries")
    def list_entries(self, request, uuid=None):
        feedback_request = self.get_object()
        entries = Feedback.objects.filter(feedback_request=feedback_request)
        serializer = FeedbackSerializer(
            entries, many=True, context={"request": request}
        )
        return Response(serializer.data)


class FeedbackEntryViewSet(viewsets.ModelViewSet):
    """Endpoint for sending feedback (ad-hoc or answer)."""

    lookup_field = "uuid"
    queryset = Feedback.objects.all().select_related("note")
    serializer_class = FeedbackSerializer
    permission_classes = [FeedbackEntryPermission]

    def get_queryset(self):
        user = self.request.user
        return (
            self.queryset.select_related("note")
            .prefetch_related("note__mentioned_users")
            .filter(
                Q(sender=user)
                | Q(receiver=user)
                | Q(feedback_request__note__owner=user)  # requester sees answers
                | (Q(feedback_request__isnull=True) & Q(note__mentioned_users=user))
            )
            .distinct()
        )


# ─────────────────────────────────────

__all__ = [
    "FeedbackFormViewSet",
    "FeedbackRequestViewSet",
    "FeedbackEntryViewSet",
]
