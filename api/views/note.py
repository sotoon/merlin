from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import (Feedback, Note, NoteType, NoteUserAccess, Summary, OneOnOne, UserTimeline)
from api.permissions import FeedbackPermission, NotePermission, SummaryPermission, HasOneOnOneAccess, IsCurrentCycleEditable, IsLeaderForMember
from api.serializers import (
    FeedbackSerializer,
    NoteSerializer,
    SummarySerializer,
    OneOnOneSerializer,
)
from api.services import get_notes_visible_to
from api.views.mixins import CycleQueryParamMixin


__all__ = ['NoteViewSet', 'TemplatesView', 'FeedbackViewSet', 'SummaryViewSet', 'OneOnOneViewSet', 'MyOneOnOneViewSet']


class NoteViewSet(CycleQueryParamMixin, viewsets.ModelViewSet):
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
        accessible_notes = get_notes_visible_to(self.request.user)
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


class FeedbackViewSet(CycleQueryParamMixin, viewsets.ModelViewSet):
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


class SummaryViewSet(CycleQueryParamMixin, viewsets.ModelViewSet):
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


class OneOnOneViewSet(CycleQueryParamMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """CRUD for 1-on-1 sessions *within* `/my-team/<member_id>/`."""

    serializer_class = OneOnOneSerializer
    permission_classes = (permissions.IsAuthenticated, HasOneOnOneAccess, IsCurrentCycleEditable, IsLeaderForMember)
    lookup_field = 'pk'

    # Fetches user form the id in the url, with a guard-rail
    def _load_member(self):
        from api.models.user import User
        self.member_obj = User.objects.get(uuid=self.kwargs["member_pk"])

        if self.request.method != "POST":
            if (
                self.member_obj.leader_id != self.request.user.id
                and self.member_obj.id != self.request.user.id
            ):
                raise PermissionDenied("Not your direct report")

    # Loads member_obj once, and stores it on self before any list/create/detail methods
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if "member_pk" in self.kwargs:
            self._load_member()

    # Injecting the loaded member into context, so the create() attach the correct FK automatically
    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        if hasattr(self, "member_obj"):
            ctx["member"] = self.member_obj
        return ctx

    # Log in the UserTimeline
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().create(request, *args, **kwargs)
            if response.status_code == 201:
                one_on_one_id = response.data.get('id')
                ooo = OneOnOne.objects.get(id=one_on_one_id)
                
                # Log to UserTimeline
                UserTimeline.objects.create(
                    user=ooo.member,
                    event_type='1on1_created',
                    cycle=ooo.cycle,
                    object_id=ooo.note.id,
                    extra_json={
                        "performance_summary": ooo.performance_summary,
                        "leader_id": str(ooo.note.owner.uuid),
                        "member_id": str(ooo.member.uuid),
                    },
                )
            return response

    def get_queryset(self):
        qs = OneOnOne.objects.select_related("member", "cycle", "note")

        if "member_pk" in self.kwargs:
            if self.request.user == self.member_obj:
                # Member: list / detail all their 1-on-1s (no owner filter)
                qs = qs.filter(member=self.member_obj)
            else:
                # Leader: only sessions where they are the owner
                qs = qs.filter(member=self.member_obj,
                            note__owner=self.request.user)

        return super().filter_queryset(qs)
    
    # Allows PATCH from the member, only if they are changing member_vibe
    def partial_update(self, request, *args, **kwargs):
        """
        Custom PATCH method for OneOnOne.
        - Only the member can PATCH their own member_vibe (and nothing else).
        - The leader cannot PATCH member_vibe.
        - Nobody else can PATCH at all.
        - Every valid update is logged in UserTimeline for history/auditing.
        """
        instance = self.get_object()
        user = request.user
        is_leader = (user == instance.note.owner)
        is_member = (user == instance.member)

        patch_fields = set(request.data.keys())

        # Permission checks
        if is_member:
            # Member can ONLY update their own member_vibe
            if not patch_fields.issubset({"member_vibe"}):
                raise PermissionDenied("Members may only edit their own vibe.")
        elif is_leader:
            # Leader can update anything EXCEPT member_vibe
            if "member_vibe" in patch_fields:
                raise PermissionDenied("Leaders may not edit member vibe.")
        else:
            # No other users allowed
            raise PermissionDenied("Not authorized to edit this 1:1.")
        
        return super().partial_update(request, *args, **kwargs)

    # Log in the UserTimeline
    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().update(request, *args, **kwargs)
            if response.status_code in (200, 202):
                one_on_one_id = response.data.get('id')

                ooo = OneOnOne.objects.get(id=one_on_one_id)
                UserTimeline.objects.create(
                    user=ooo.member,
                    event_type='1on1_updated',
                    cycle=ooo.cycle,
                    object_id=ooo.note.id,
                    extra_json={
                        "performance_summary": ooo.performance_summary,
                        "leader_id": str(ooo.note.owner.uuid),
                        "member_id": str(ooo.member.uuid),
                    },
                )

            return response


class MyOneOnOneViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = OneOnOneSerializer
    permission_classes = (IsAuthenticated, HasOneOnOneAccess)

    def get_queryset(self):
        return OneOnOne.objects.select_related("note").filter(member=self.request.user)
