from django.db.models import Max, Count, Q
from rest_framework import permissions, viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db import models

from api.services.timeline_access import can_view_timeline
from api.models import User, Cycle, Ladder, SenioritySnapshot
from api.serializers.profile import (
    ProfileSerializer,
    ProfileListSerializer,
    CurrentLadderSerializer,
    LadderListSerializer,
)
from api.models.ladder import LadderStage


__all__ = [
    "ProfileView",
    "UserListView",
    "UserDetailView",
    "MyTeamViewSet",
    "CurrentLadderView",
    "LadderListView",
]


class ProfileView(RetrieveUpdateAPIView):
    """
    Update or read Profile data
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer
    queryset = User.objects.all()


class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    lookup_field = "uuid"


class MyTeamViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of the current user's direct reports with 1:1 metadata, for the current cycle."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        leader = self.request.user
        cycle = Cycle.get_current_cycle()
        qs = User.objects.filter(leader=leader)

        if cycle is not None:
            qs = qs.annotate(
                latest_oneonone=Max(
                    "one_on_ones__note__date",
                    filter=Q(
                        one_on_ones__note__owner=leader,
                        one_on_ones__cycle=cycle,
                    ),
                ),
                oneonone_count=Count(
                    "one_on_ones",
                    filter=Q(
                        one_on_ones__note__owner=leader,
                        one_on_ones__cycle=cycle,
                    ),
                ),
            )

        return qs


class CurrentLadderView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CurrentLadderSerializer

    def get(self, request, user_uuid=None):
        # Determine target user
        if user_uuid is None:
            target = request.user
        else:
            target = get_object_or_404(User, uuid=user_uuid)

        # Permission check using existing timeline ACL
        if not can_view_timeline(request.user, target):
            raise PermissionDenied("شما اجازه مشاهده این بخش را ندارید")

        snapshot = (
            SenioritySnapshot.objects.filter(user=target)
            .order_by("-effective_date", "-date_created")
            .first()
        )
        ladder = snapshot.ladder if snapshot else Ladder.objects.first()
        aspects = ladder.aspects.order_by("order").values("code", "name")
        stages = [{"value": v, "label": l} for v, l in LadderStage.choices]

        data = {"ladder": ladder.code, "max_level": ladder.get_max_level(), "aspects": list(aspects), "stages": stages}
        serializer = self.serializer_class(data=data)
        serializer.is_valid()
        return Response(serializer.validated_data)


class LadderListView(ListAPIView):
    """Return all available ladders with their aspects."""
    permission_classes = [IsAuthenticated]
    serializer_class = LadderListSerializer
    queryset = Ladder.objects.prefetch_related('aspects').all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = []
        
        for ladder in queryset:
            aspects = ladder.aspects.order_by("order").values("code", "name")
            stages = [{"value": v, "label": l} for v, l in LadderStage.choices]
            serializer = self.get_serializer({
                "code": ladder.code,
                "name": ladder.name,
                "description": ladder.description,
                "max_level": ladder.get_max_level(),
                "aspects": list(aspects),
                "stages": stages,
            })
            data.append(serializer.data)
        
        return Response(data)
