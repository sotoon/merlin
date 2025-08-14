from rest_framework import generics, permissions

from api.models import ValueTag, Team
from api.serializers import TagReadSerializer, TeamSerializer


__all__ = ['ValueTagListView', 'TeamListView']


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
    