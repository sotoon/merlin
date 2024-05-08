import re

from rest_framework import serializers

from api.models import Feedback, Note, NoteUserAccess, Summary, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("uuid", "name", "email", "password")
        write_only_fields = ["password"]
        read_only_fields = ["uuid"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()


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
    class Meta:
        model = User
        fields = (
            "uuid",
            "email",
            "name",
        )


class NoteUserAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteUserAccess
        fields = [
            "can_view",
            "can_edit",
            "can_view_summary",
            "can_write_summary",
            "can_write_feedback",
        ]


class NoteSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(), read_only=True, slug_field="email"
    )
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    mentioned_users = serializers.SlugRelatedField(
        many=True, required=False, queryset=User.objects.all(), slug_field="email"
    )
    linked_notes = serializers.SlugRelatedField(
        many=True, required=False, queryset=Note.objects.all(), slug_field="uuid"
    )
    read_status = serializers.SerializerMethodField()
    access_level = serializers.SerializerMethodField()
    content_preview = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Note
        fields = (
            "uuid",
            "date_created",
            "date_updated",
            "owner",
            "owner_name",
            "title",
            "content",
            "content_preview",
            "date",
            "period",
            "year",
            "type",
            "mentioned_users",
            "linked_notes",
            "read_status",
            "access_level",
        )
        read_only_fields = [
            "uuid",
            "date_created",
            "date_updated",
            "read_status",
            "access_level",
        ]

    def validate(self, data):
        if not self.instance:
            owner = self.context["request"].user
            data["owner"] = owner
        return super().validate(data)

    def get_read_status(self, obj):
        user = self.context["request"].user
        return obj.read_by.filter(uuid=user.uuid).exists()

    def get_access_level(self, obj):
        user = self.context["request"].user
        access_level = NoteUserAccess.objects.filter(user=user, note=obj).first()
        if access_level:
            return NoteUserAccessSerializer(access_level).data
        return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and request.method == "GET":
            data.pop("content_preview", None)
        return data

    def create(self, validated_data):
        content = validated_data.get("content", None)
        if content:
            text_content = re.sub("<.*?>", " ", content)
            validated_data["content_preview"] = text_content[:200]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        content = validated_data.get("content", None)
        if content:
            text_content = re.sub("<.*?>", " ", content)
            validated_data["content_preview"] = text_content[:200]
        return super().update(instance, validated_data)


class NoteListSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(), read_only=True, slug_field="email"
    )
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    read_status = serializers.SerializerMethodField()
    access_level = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = (
            "uuid",
            "date_created",
            "date_updated",
            "owner",
            "owner_name",
            "title",
            "content_preview",
            "date",
            "period",
            "year",
            "type",
            "read_status",
            "access_level",
        )
        read_only_fields = [
            "uuid",
            "date_created",
            "date_updated",
            "read_status",
            "access_level",
        ]

    def validate(self, data):
        if not self.instance:
            owner = self.context["request"].user
            data["owner"] = owner
        return super().validate(data)

    def get_read_status(self, obj):
        user = self.context["request"].user
        return obj.read_by.filter(uuid=user.uuid).exists()

    def get_access_level(self, obj):
        user = self.context["request"].user
        access_level = NoteUserAccess.objects.filter(user=user, note=obj).first()
        if access_level:
            return NoteUserAccessSerializer(access_level).data
        return None


class FeedbackSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
        slug_field="email",
    )
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    note = serializers.SlugRelatedField(read_only=True, slug_field="uuid")

    class Meta:
        model = Feedback
        fields = (
            "uuid",
            "owner",
            "owner_name",
            "note",
            "content",
        )
        read_only_fields = ["uuid"]

    def validate(self, data):
        note_uuid = self.context["note_uuid"]
        data["note"] = Note.objects.get(uuid=note_uuid)
        return super().validate(data)

    def create(self, validated_data):
        user = validated_data["owner"]
        note = validated_data["note"]
        content = validated_data["content"]
        feedback, created = Feedback.objects.update_or_create(
            owner=user, note=note, defaults={"content": content}
        )
        return feedback


class SummarySerializer(serializers.ModelSerializer):
    note = serializers.SlugRelatedField(read_only=True, slug_field="uuid")

    class Meta:
        model = Summary
        fields = (
            "uuid",
            "note",
            "content",
            "performance_label",
            "ladder_change",
            "bonus",
            "salary_change",
            "committee_date",
        )
        read_only_fields = ["uuid"]

    def validate(self, data):
        note_uuid = self.context["note_uuid"]
        data["note"] = Note.objects.get(uuid=note_uuid)
        return super().validate(data)

    def create(self, validated_data):
        instance, created = Summary.objects.update_or_create(
            note=validated_data["note"], defaults=validated_data
        )
        return instance
