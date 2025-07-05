from rest_framework import generics, permissions

from api.models import ValueTag
from api.serializers import TagReadSerializer


__all__ = ['ValueTagListView']


class ValueTagListView(generics.ListAPIView):
    """Catalog endpoint for value tags + sections."""
    queryset = ValueTag.objects.all()
    serializer_class = TagReadSerializer
    permission_classes = (permissions.IsAuthenticated,)