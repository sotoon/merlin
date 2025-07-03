from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from api.services import grant_oneonone_access
from api.serializers.organization import TagReadSerializer
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
    UserTimeline,
)


__all__ = [
    "NoteUserAccessSerializer",
    "NoteSerializer",
    "FeedbackSerializer",
    "SummarySerializer",
    "OneOnOneSerializer",
    "OneOnOneTagLinkReadSerializer",
]


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
    access_level = NoteUserAccessSerializer(read_only=True, allow_null=True)
    one_on_one_member = serializers.SlugRelatedField(
        source="one_on_one.member", read_only=True, slug_field="uuid"
    )
    one_on_one_id = serializers.IntegerField(source="one_on_one.id", read_only=True)

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
            "one_on_one_member",
            "one_on_one_id",
        )
        read_only_fields = [
            "uuid",
            "date_created",
            "date_updated",
            "read_status",
            "access_level",
            "one_on_one_member",
            "one_on_one_id",
        ]

    def validate(self, data):
        if not self.instance:
            owner = self.context["request"].user
            data["owner"] = owner
        return super().validate(data)

    def validate_mentioned_users(self, value):
        """
        Disallow mentioning yourself.
        `value` is a QuerySet/list of User instances the client sent.
        """
        request_user = self.context["request"].user
        if request_user in value:
            raise serializers.ValidationError(
                _("You cannot mention yourself in a note.")
            )
        return value

    def get_read_status(self, obj):
        user = self.context["request"].user
        return obj.read_by.filter(uuid=user.uuid).exists()

    def to_representation(self, instance):
        user = self.context["request"].user
        access_level_obj = NoteUserAccess.objects.filter(
            user=user, note=instance
        ).first()
        instance.access_level = access_level_obj
        return super().to_representation(instance)


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
        read_only_fields = [
            "uuid",
        ]

    def validate(self, data):
        note_uuid = self.context["note_uuid"]
        data["note"] = Note.objects.get(uuid=note_uuid)
        return super().validate(data)

    def create(self, validated_data):
        instance, created = Summary.objects.update_or_create(
            note=validated_data["note"], defaults=validated_data
        )
        return instance


# Used for analytics endpoints
class OneOnOneTagLinkReadSerializer(serializers.ModelSerializer):
    """
    Read-only: return tag/section per link on each 1:1
    """

    tag = TagReadSerializer()

    class Meta:
        model = OneOnOneTagLink
        fields = ["id", "tag", "section"]


class OneOnOneSerializer(serializers.ModelSerializer):
    """
    Handles 1:1 CRUD with:
    - Client sends 'tags': [id, ...]
    - Server creates Note, OneOnOne, TagLinks in a single transaction
    - 'tag_links' read-only for analytics/reporting
    - 'note_meta' nested for UI

    Privacy logic:
    The leader and member should not see each other's 'vibe' feedback. In the to_representation method,
    we remove 'member_vibe' from the output if the current user is the leader, and remove 'leader_vibe'
    if the current user is the member. This ensures privacy and prevents bias or retaliation.
    """

    note = NoteSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ValueTag.objects.filter(orgvaluetag__is_enabled=True)
    )
    tag_links = OneOnOneTagLinkReadSerializer(
        source="oneononetaglink_set", many=True, read_only=True
    )
    linked_notes = serializers.SlugRelatedField(
        many=True, required=False, queryset=Note.objects.all(), slug_field="uuid"
    )
    # member_id injects by the ViewSet

    class Meta:
        model = OneOnOne
        fields = [
            "id",
            "note",
            "member",
            "cycle",
            "personal_summary",
            "career_summary",
            "performance_summary",
            "communication_summary",
            "actions",
            "leader_vibe",
            "member_vibe",
            "linked_notes",
            "tags",  # input/output: flat list of IDs
            "tag_links",  # output: sectioned/grouped per 1:1 instance
            "extra_notes",
            "date_created",
            "date_updated",
            "uuid",
        ]
        read_only_fields = (
            "id",
            "member",
            "cycle",
            "date_created",
            "date_updated",
            "uuid",
        )
        # Make member_vibe non-required
        extra_kwargs = {
            "member_vibe": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        linked_notes = validated_data.pop("linked_notes", [])
        request = self.context["request"]
        validated_data.pop("cycle", None)
        cycle = Cycle.get_current_cycle()
        member = self.context["member"]  # injected by ViewSet

        with transaction.atomic():
            note = Note.objects.create(
                owner=request.user,
                title=f"1:1 • {member}",
                content="",
                date=validated_data.get("date", timezone.now().date()),
                type=NoteType.ONE_ON_ONE,
                cycle=cycle,
            )
            note.linked_notes.set(linked_notes)
            oneonone = OneOnOne.objects.create(
                note=note, member=member, cycle=cycle, **validated_data
            )
            for tag in tags:
                OneOnOneTagLink.objects.create(
                    one_on_one=oneonone, tag=tag, section=tag.section
                )
            grant_oneonone_access(oneonone.note)

        return oneonone

    def update(self, instance, validated_data):
        """
        Update OneOnOne, Note.linked_notes, Note.mentioned_users, and TagLinks.
        Tag links are fully replaced; section always comes from tag.section.
        """
        tags = validated_data.pop("tags", None)
        linked_notes = validated_data.pop("linked_notes", None)

        with transaction.atomic():
            oneonone = super().update(instance, validated_data)
            note = oneonone.note

            if linked_notes is not None:
                note.linked_notes.set(linked_notes)

            if tags is not None:
                OneOnOneTagLink.objects.filter(one_on_one=oneonone).delete()
                for tag in tags:
                    OneOnOneTagLink.objects.create(
                        one_on_one=oneonone, tag=tag, section=tag.section
                    )
        grant_oneonone_access(oneonone.note)
        return oneonone

    # Prevent leader and member to access each others vibe marks
    def to_representation(self, instance):
        data = super().to_representation(instance)
        user = self.context["request"].user
        # Privacy logic: Only show the user's own vibe, not the other party's
        if instance.note.owner_id == user.id:
            # Leader should not see member's vibe
            data.pop("member_vibe", None)
        elif instance.member_id == user.id:
            # Member should not see leader's vibe
            data.pop("leader_vibe", None)
        return data
