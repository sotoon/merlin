from django.db.models import Max, Count, Q
from rest_framework import permissions, viewsets
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import User, Cycle
from api.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
)


__all__ = ['ProfileView', 'UsersView', 'MyTeamViewSet']


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


class UsersView(ListAPIView):
    """
    List all app users
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        return User.objects.all()


class MyTeamViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only list of the current user's direct reports with 1:1 metadata, for the current cycle."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_queryset(self):
        leader = self.request.user
        cycle  = Cycle.get_current_cycle()
        return (
            User.objects.filter(leader=leader)
            .annotate(
                latest_oneonone=Max(
                    "one_on_ones__note__date",
                    filter=Q(one_on_ones__note__owner=leader,
                             one_on_ones__cycle=cycle,
                             ),
                    
                ),
                oneonone_count=Count(
                    "one_on_ones",
                    filter=Q(one_on_ones__note__owner=leader,
                             one_on_ones__cycle=cycle,
                             ),
                ),
            )
        )