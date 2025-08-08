from rest_framework import serializers

from api.models import (
    User,
    Ladder,
)
from api.utils.timeline import get_current_job_title


__all__ = [
    "UserSerializer",
    "ProfileSerializer",
    "ProfileListSerializer",
    "CurrentLadderSerializer",
    "LadderSerializer",
    "LadderListSerializer",
]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uuid", "name", "email", "password")
        write_only_fields = ["password"]
        read_only_fields = ["uuid"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(read_only=True, slug_field="name")
    chapter = serializers.SlugRelatedField(read_only=True, slug_field="name")
    team = serializers.SlugRelatedField(read_only=True, slug_field="name")
    leader = serializers.SlugRelatedField(read_only=True, slug_field="name")
    current_job_title = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "uuid",
            "email",
            "name",
            "gmail",
            "phone",
            "department",
            "chapter",
            "team",
            "leader",
            "current_job_title",
        )
        read_only_fields = [
            "id",
            "uuid",
            "email",
            "department",
            "chapter",
            "team",
            "leader",
            "current_job_title",
        ]

    def get_current_job_title(self, obj):
        return get_current_job_title(obj)


class ProfileListSerializer(serializers.ModelSerializer):
    team = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = User
        fields = ("uuid", "email", "name", "team")


class AspectSerializer(serializers.Serializer):
    """Serializer for ladder aspect with code and name."""

    code = serializers.CharField(help_text="Aspect code (e.g., 'DES', 'IMP', 'BUS')")
    name = serializers.CharField(help_text="Aspect name")


class CurrentLadderSerializer(serializers.Serializer):
    """Serializer for current ladder and aspects response."""

    ladder = serializers.CharField(help_text="Ladder code (e.g., 'SW', 'DEVOPS')")
    max_level = serializers.IntegerField(help_text="Maximum level for this ladder")
    aspects = AspectSerializer(
        many=True, help_text="List of ladder aspects with their codes and names"
    )


class LadderSerializer(serializers.ModelSerializer):
    """Serializer for a single ladder with its aspects."""
    
    aspects = AspectSerializer(many=True, read_only=True)
    max_level = serializers.SerializerMethodField(help_text="Maximum level for this ladder")
    
    class Meta:
        model = Ladder
        fields = ("code", "name", "description", "aspects", "max_level")
        read_only_fields = ("code", "name", "description", "aspects", "max_level")
    
    def get_max_level(self, obj):
        return obj.get_max_level()


class LadderListSerializer(serializers.Serializer):
    """Serializer for list of ladders with their aspects."""
    
    code = serializers.CharField(help_text="Ladder code (e.g., 'SW', 'DEVOPS')")
    name = serializers.CharField(help_text="Ladder name")
    description = serializers.CharField(help_text="Ladder description")
    max_level = serializers.IntegerField(help_text="Maximum level for this ladder")
    aspects = AspectSerializer(many=True, help_text="List of ladder aspects with their codes and names")
