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

    List endpoint supports filters:
        • ?type=owned    requests user created
        • ?type=invited  requests user should answer
        • ?type=all      all requests (default)
    """

    queryset = FeedbackRequest.objects.all()
    permission_classes = [FeedbackRequestPermission]
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return FeedbackRequestReadOnlySerializer
        return FeedbackRequestWriteSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.select_related("note", "note__owner").prefetch_related(
            "requestees__user"
        )

        # Handle type filter
        request_type = self.request.query_params.get("type", "all")

        if request_type == "owned":
            queryset = queryset.filter(note__owner=user)
        elif request_type == "invited":
            queryset = queryset.filter(requestees__user=user).exclude(note__owner=user)
        # For "all" or any other value, return all requests the user has access to
        else:
            queryset = queryset.filter(
                Q(note__owner=user) | Q(requestees__user=user)
            ).distinct()

        return queryset

    def create(self, request, *args, **kwargs):
        """Create a feedback request and mark the note as read for the creator."""
        response = super().create(request, *args, **kwargs)

        # Mark the note as read for the user who created the feedback request
        feedback_request = FeedbackRequest.objects.get(uuid=response.data["uuid"])
        note = feedback_request.note
        user = request.user

        if user not in note.read_by.all():
            note.read_by.add(user)

        return response

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
        queryset = (
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

        # Handle ad-hoc filter
        is_adhoc = self.request.query_params.get("adhoc", "").lower() == "true"
        if is_adhoc:
            queryset = queryset.filter(feedback_request__isnull=True)

        return queryset


# ─────────────────────────────────────

__all__ = [
    "FeedbackFormViewSet",
    "FeedbackRequestViewSet",
    "FeedbackEntryViewSet",
]
