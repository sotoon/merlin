from rest_framework import serializers

from api.models import ValueTag, Team, Tribe


__all__ = ['TagReadSerializer', 'TeamSerializer']


# Tag catalogue: lets frontend fetch all tags with their section
class TagReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for /value-tags/ -- lets the client fetch all tags with their section."""
    class Meta:
        model = ValueTag
        fields = ["id", "name_en", "name_fa", "section"]


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["id", "name"]


class TribeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tribe
    fields = ["id", "name"]