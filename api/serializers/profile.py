from rest_framework import serializers

from api.models import (
    User,
)


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

    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "name",
            "gmail",
            "phone",
            "department",
            "chapter",
            "team",
            "leader",
            "level",
        )
        read_only_fields = [
            "uuid",
            "email",
            "department",
            "chapter",
            "team",
            "leader",
            "level",
        ]


class ProfileListSerializer(serializers.ModelSerializer):
    team = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = User
        fields = ("uuid", "email", "name", "team")
