from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Feedback, Note, NoteType, NoteUserAccess, Summary
from api.permissions import FeedbackPermission, NotePermission, SummaryPermission
from api.serializers import (
    FeedbackSerializer,
    NoteSerializer,
    SummarySerializer,
)


__all__ = ['NoteViewSet', 'TemplatesView', 'FeedbackViewSet', 'SummaryViewSet']


class NoteViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = NoteSerializer
    permission_classes = (IsAuthenticated, NotePermission)
    search_fields = ["type"]

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Note, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user_email = self.request.query_params.get("user")
        retrieve_mentions = self.request.query_params.get("retrieve_mentions")
        accessible_note_ids = NoteUserAccess.objects.filter(
            user=self.request.user, can_view=True
        ).values_list("note__uuid", flat=True)
        accessible_notes = Note.objects.filter(uuid__in=accessible_note_ids)
        if user_email:
            queryset = accessible_notes.filter(owner__email=user_email)
        elif retrieve_mentions:
            queryset = accessible_notes.filter(~Q(owner=self.request.user))
        else:
            queryset = accessible_notes.filter(owner=self.request.user)
        type = self.request.query_params.get("type")
        if type:
            queryset = queryset.filter(type=type)
        return queryset.distinct()

    @action(detail=True, methods=["post"], url_path="read")
    def mark_note_as_read(self, request, uuid=None):
        """
        Mark note as read(Does not need any input params)
        """
        note = self.get_object()
        user = request.user
        if user not in note.read_by.all():
            note.read_by.add(user)
            return Response(
                {"status": "Note marked as read for the current user."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "Note is already marked as read for the current user."},
                status=status.HTTP_200_OK,
            )

    @action(detail=True, methods=["post"], url_path="unread")
    def mark_note_as_unread(self, request, uuid=None):
        """
        Mark note as unread(Does not need any input params)
        """
        note = self.get_object()
        user = request.user
        if user in note.read_by.all():
            note.read_by.remove(user)
            return Response(
                {"status": "Note marked as unread for the current user."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "Note is already marked as unread for the current user."},
                status=status.HTTP_200_OK,
            )


class TemplatesView(ListAPIView):
    """
    List available templates
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        user_templates = Note.objects.filter(
            type=NoteType.Template, owner=self.request.user
        )
        public_templates = Note.objects.filter(type=NoteType.Template, is_public=True)
        return (user_templates | public_templates).distinct()


class FeedbackViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, FeedbackPermission]
    search_fields = ["owner"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"note_uuid": self.kwargs.get("note_uuid", None)})
        return context

    def get_note(self):
        return get_object_or_404(
            Note,
            uuid=self.kwargs["note_uuid"],
        )

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Feedback, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        current_note = self.get_note()
        all_note_feedbacks = Feedback.objects.filter(note=current_note).distinct()
        owner_email = self.request.query_params.get("owner")
        if owner_email:
            all_note_feedbacks = all_note_feedbacks.filter(owner__email=owner_email)
        if NoteUserAccess.objects.filter(
            note=current_note, user=self.request.user, can_view_feedbacks=True
        ).exists():
            return all_note_feedbacks
        return all_note_feedbacks.filter(owner=self.request.user)


class SummaryViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated, SummaryPermission]
    search_fields = ["owner"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"note_uuid": self.kwargs.get("note_uuid", None)})
        return context

    def get_note(self):
        return get_object_or_404(
            Note,
            uuid=self.kwargs["note_uuid"],
        )

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Summary, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        current_note = self.get_note()
        if NoteUserAccess.objects.filter(
            note=current_note, user=self.request.user, can_view_summary=True
        ).exists():
            return Summary.objects.filter(note=current_note)
        return Summary.objects.none()
