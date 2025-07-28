from rest_framework import serializers

from api.models import (
    User,
)
from api.utils.timeline import get_current_job_title


__all__ = ["UserSerializer", "ProfileSerializer", "ProfileListSerializer"]


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
