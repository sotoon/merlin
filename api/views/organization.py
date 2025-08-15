from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from api.models import ValueTag, Team, Tribe
from api.serializers import TagReadSerializer
from api.serializers.organization import (
    TeamSerializer,
    TribeSerializer,
)


__all__ = ['ValueTagListView', 'TeamListView', 'TribeListView']


class ValueTagListView(generics.ListAPIView):
    """Catalog endpoint for value tags + sections."""
    queryset = ValueTag.objects.all()
    serializer_class = TagReadSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TeamListView(generics.ListAPIView):
    """Catalog endpoint for all teams."""
    queryset = Team.objects.all().order_by('name')
    serializer_class = TeamSerializer
    permission_classes = (permissions.IsAuthenticated,)


class TribeListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TribeSerializer
    queryset = Tribe.objects.all()
    