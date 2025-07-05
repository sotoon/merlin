from rest_framework import serializers

from api.models import ValueTag


__all__ = ['TagReadSerializer']


# Tag catalogue: lets frontend fetch all tags with their section
class TagReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for /value-tags/ -- lets the client fetch all tags with their section."""
    class Meta:
        model = ValueTag
        fields = ["id", "name_en", "name_fa", "section"]
