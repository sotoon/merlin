from rest_framework import serializers

from api.models import Note, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        write_only_fields = ["password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(), read_only=True
    )

    class Meta:
        model = Note
        fields = ("uuid", "owner", "title", "content", "date", "type")
        read_only_fields = ["uuid"]

    def validate(self, data):
        if not self.instance:
            owner = self.context["request"].user
            data["owner"] = owner
        return super().validate(data)


class ProfileSerializer(serializers.ModelSerializer):
    department = serializers.SlugRelatedField(read_only=True, slug_field="name")
    chapter = serializers.SlugRelatedField(read_only=True, slug_field="name")
    team = serializers.SlugRelatedField(read_only=True, slug_field="name")
    leader = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "name",
            "gmail",
            "phone",
            "department",
            "chapter",
            "team",
            "leader",
        )
        read_only_fields = [
            "username",
            "email",
            "department",
            "chapter",
            "team",
            "leader",
        ]
