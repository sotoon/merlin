from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from api.models import (
    Comment,
    Note,
    NoteType,
    NoteUserAccess,
    Summary,
    OneOnOne,
    OneOnOneActivityLog,
)
from api.permissions import (
    CommentPermission as FeedbackPermission,
    NotePermission,
    SummaryPermission,
    HasOneOnOneAccess,
    IsCurrentCycleEditable,
    IsLeaderForMember,
)
from api.serializers import (
    CommentSerializer,
    NoteSerializer,
    SummarySerializer,
    OneOnOneSerializer,
)
from api.services import get_notes_visible_to
from api.views.mixins import CycleQueryParamMixin


__all__ = [
    "NoteViewSet",
    "TemplatesView",
    "CommentViewSet",
    "FeedbackViewSet",
    "SummaryViewSet",
    "OneOnOneViewSet",
    "MyOneOnOneViewSet",
]


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
        note_type_filter = self.request.query_params.get("type")
        proposal_type_filter = self.request.query_params.get("proposal_type")

        accessible_notes = get_notes_visible_to(self.request.user)

        if user_email:
            queryset = accessible_notes.filter(owner__email=user_email)

        elif retrieve_mentions:
            # Get all accessible notes user doesn't own
            queryset = accessible_notes.filter(~Q(owner=self.request.user))
            
            # EXCLUDE feedback answers where user is only mentioned in parent REQUEST
            # (not the receiver). This prevents phantom notifications for "observer" mentions.
            # User can still access these answers via /feedback-requests/{uuid}/entries/
            queryset = queryset.exclude(
                Q(type=NoteType.FEEDBACK) &
                Q(feedback__feedback_request__isnull=False) &  # It's an answer (has parent request)
                ~Q(feedback__receiver=self.request.user)  # User is NOT the receiver
            )

        else:
            queryset = accessible_notes.filter(owner=self.request.user)

            # ALSO include feedback the user received
            queryset = queryset | accessible_notes.filter(
                type=NoteType.FEEDBACK, feedback__receiver=self.request.user
            )

            # ALSO include 1-on-1s where the user is the member
            queryset = queryset | accessible_notes.filter(
                type=NoteType.ONE_ON_ONE, one_on_one__member=self.request.user
            )

        if note_type_filter:
            queryset = queryset.filter(type=note_type_filter)

        if proposal_type_filter:
            queryset = queryset.filter(proposal_type=proposal_type_filter)

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


class CommentViewSet(CycleQueryParamMixin, viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = CommentSerializer
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
        obj = get_object_or_404(Comment, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        current_note = self.get_note()
        all_note_feedbacks = Comment.objects.filter(note=current_note).distinct()
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


class OneOnOneViewSet(
    CycleQueryParamMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD for 1-on-1 sessions *within* `/my-team/<member_id>/`."""

    serializer_class = OneOnOneSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        HasOneOnOneAccess,
        IsCurrentCycleEditable,
        IsLeaderForMember,
    )
    lookup_field = "pk"

    # Fetches user form the id in the url, with a guard-rail
    def _load_member(self):
        from api.models.user import User

        self.member_obj = User.objects.get(uuid=self.kwargs["member_pk"])

        if self.request.method != "POST":
            if (
                self.member_obj.leader_id != self.request.user.id
                and self.member_obj.id != self.request.user.id
            ):
                raise PermissionDenied(
                    _("You do not have access to this direct report's one-on-ones.")
                )

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

    # Log activity
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().create(request, *args, **kwargs)
            if response.status_code == 201:
                one_on_one_id = response.data.get("id")
                ooo = OneOnOne.objects.get(id=one_on_one_id)

                # Log activity
                OneOnOneActivityLog.objects.create(
                    user=ooo.member,
                    event_type="1on1_created",
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
        qs = OneOnOne.objects.select_related(
            "member", "cycle", "note"
        ).prefetch_related("tags", "note__linked_notes")
        if "member_pk" in self.kwargs:
            if self.request.user == self.member_obj:
                qs = qs.filter(member=self.member_obj)
            else:
                qs = qs.filter(member=self.member_obj, note__owner=self.request.user)

        # Search functionality
        search = self.request.query_params.get("search", "")
        if search:
            qs = qs.filter(
                Q(note__title__icontains=search)
                | Q(personal_summary__icontains=search)
                | Q(career_summary__icontains=search)
                | Q(communication_summary__icontains=search)
                | Q(performance_summary__icontains=search)
                | Q(actions__icontains=search)
                | Q(extra_notes__icontains=search)
            )

        # Date range filtering
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(date_created__gte=date_from)
        if date_to:
            qs = qs.filter(date_created__lte=date_to)

        # Sort functionality
        sort = self.request.query_params.get("sort", "newest")
        if sort == "oldest":
            qs = qs.order_by("date_created")
        elif sort == "title":
            qs = qs.order_by("note__title")
        else:  # default: 'newest'
            qs = qs.order_by("-date_created")

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
        is_leader = user == instance.note.owner
        is_member = user == instance.member

        patch_fields = set(request.data.keys())

        # Permission checks
        if is_member:
            # Member can ONLY update their own member_vibe
            if not patch_fields.issubset({"member_vibe"}):
                raise PermissionDenied(
                    _("Members may only edit their own vibe (member_vibe).")
                )
        elif is_leader:
            # Leader can update anything EXCEPT member_vibe
            if "member_vibe" in patch_fields:
                raise PermissionDenied(
                    _("Leaders may not edit the member's vibe (member_vibe).")
                )
        else:
            # No other users allowed
            raise PermissionDenied(_("You are not authorized to edit this one-on-one."))

        return super().partial_update(request, *args, **kwargs)

    # Log activity
    def update(self, request, *args, **kwargs):
        with transaction.atomic():
            response = super().update(request, *args, **kwargs)
            if response.status_code in (200, 202):
                one_on_one_id = response.data.get("id")

                ooo = OneOnOne.objects.get(id=one_on_one_id)
                OneOnOneActivityLog.objects.create(
                    user=ooo.member,
                    event_type="1on1_updated",
                    cycle=ooo.cycle,
                    object_id=ooo.note.id,
                    extra_json={
                        "performance_summary": ooo.performance_summary,
                        "leader_id": str(ooo.note.owner.uuid),
                        "member_id": str(ooo.member.uuid),
                    },
                )

            return response


class MyOneOnOneViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = OneOnOneSerializer
    permission_classes = (IsAuthenticated, HasOneOnOneAccess)

    def get_queryset(self):
        return (
            OneOnOne.objects.select_related("note")
            .prefetch_related("tags", "note__linked_notes")
            .filter(member=self.request.user)
        )


# Backward compatibility route alias
FeedbackViewSet = CommentViewSet
