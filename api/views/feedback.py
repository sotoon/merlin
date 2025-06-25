from rest_framework import viewsets, permissions
from api.serializers.feedback import (
    FeedbackFormSerializer,
    FeedbackRequestSerializer,
    FeedbackSerializer,
)
from api.models.note import FeedbackForm, FeedbackRequest, Feedback
from django.db import models
from api.permissions import FeedbackEntryPermission, FeedbackRequestPermission


class FeedbackFormViewSet(viewsets.ReadOnlyModelViewSet):
    """Publicly list active feedback forms."""

    queryset = FeedbackForm.objects.filter(is_active=True)
    serializer_class = FeedbackFormSerializer
    permission_classes = [permissions.IsAuthenticated]


class FeedbackRequestViewSet(viewsets.ModelViewSet):
    """CRUD for feedback requests."""

    queryset = FeedbackRequest.objects.all().select_related("note")
    serializer_class = FeedbackRequestSerializer
    permission_classes = [FeedbackRequestPermission]
    lookup_field = "uuid"

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            models.Q(note__owner=user) | models.Q(requestees__user=user)
        ).distinct()


class FeedbackEntryViewSet(viewsets.ModelViewSet):
    """Endpoint for sending feedback (ad-hoc or answer)."""

    lookup_field = "uuid"
    queryset = Feedback.objects.all().select_related("note")
    serializer_class = FeedbackSerializer
    permission_classes = [FeedbackEntryPermission]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(
            models.Q(sender=user) |
            models.Q(receiver=user) |
            (
                models.Q(request_note__isnull=True) &   # ad-hoc feedbacks only
                models.Q(note__mentioned_users=user)
            )
        ).distinct()

# ─────────────────────────────────────

__all__ = [
    "FeedbackFormViewSet",
    "FeedbackRequestViewSet",
    "FeedbackEntryViewSet",
] 