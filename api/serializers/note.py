from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

from api.utils import grant_oneonone_access
from api.models import (
        Feedback,
        Note,
        NoteType,
        NoteUserAccess,
        Summary,
        User,
        OneOnOne,
        OneOnOneTagLink,
        ValueTag,
        Cycle,
)


__all__ = ['NoteUserAccessSerializer', 'NoteSerializer', 'FeedbackSerializer', 'SummarySerializer']


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
            "date",
            "period",
            "year",
            "type",
            "mentioned_users",
            "linked_notes",
            "read_status",
            "access_level",
            "submit_status",
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
            "submit_status",
        )
        read_only_fields = ["uuid", ]

    def validate(self, data):
        note_uuid = self.context["note_uuid"]
        data["note"] = Note.objects.get(uuid=note_uuid)
        return super().validate(data)

    def create(self, validated_data):
        instance, created = Summary.objects.update_or_create(
            note=validated_data["note"], defaults=validated_data
        )
        return instance


class OneOnOneTagLinkSerializer(serializers.ModelSerializer):
    tag_id = serializers.PrimaryKeyRelatedField(queryset=ValueTag.objects.all(), source="tag", write_only=True)

    class Meta:
        model = OneOnOneTagLink
        fields = ("tag_id", "section")


class OneOnOneSerializer(serializers.ModelSerializer):
    tags = OneOnOneTagLinkSerializer(many=True, write_only=True)
    member_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="member")

    class Meta:
        model = OneOnOne
        exclude = ("organisation", "note", "created_at", "updated_at")
        read_only_fields = ("id", "cycle")

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        request = self.context["request"]
        cycle = Cycle.get_current_cycle()
        member = self.context["member"]  # injected by ViewSet


        with transaction.atomic():
            note = Note.objects.create(
                owner=request.user,
                title=f"1:1 • {validated_data['member']}",
                content="",
                date=validated_data.get("date", timezone.now().date()),
                type=NoteType.ONE_ON_ONE,
                cycle=cycle,
            )
            note.mentioned_users.add(validated_data["member"])
            oneonone = OneOnOne.objects.create(note=note, member=member, cycle=cycle, **validated_data)
            for tag in tags_data:
                OneOnOneTagLink.objects.create(one_on_one=oneonone, **tag)
            grant_oneonone_access(note)
        return oneonone

    # Prevent leader and member to access each others vibe marks
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user
        if instance.note.owner_id == user.id:
            data.pop("member_vibe", None)
        elif instance.member_id == user.id:
            data.pop("leader_vibe", None)
        return data