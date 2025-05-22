from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

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
)


__all__ = ['NoteUserAccessSerializer', 'NoteSerializer', 'FeedbackSerializer', 'SummarySerializer',
           'OneOnOneSerializer', 'OneOnOneTagLinkReadSerializer']


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


class NoteMetaSerializer(serializers.ModelSerializer):
    """Nested minimal Note info for UI convenience (title, date, mentions, links)."""
    class Meta:
        model = Note
        fields = ["id", "title", "date", "mentioned_users", "linked_notes"]


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
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=ValueTag.objects.filter(orgvaluetag__is_enabled=True)
    )
    tag_links = OneOnOneTagLinkReadSerializer(
        source="oneononetaglink_set", many=True, read_only=True
    )
    note_meta = NoteMetaSerializer(source="note", read_only=True)
    linked_notes = serializers.SlugRelatedField(
        many=True,
        required=False,
        queryset=Note.objects.all(),
        slug_field="uuid"
    )
    mentioned_users = serializers.SlugRelatedField(
        many=True,
        required=False,
        queryset=User.objects.all(),
        slug_field="email"
    )
    # member_id injects by the ViewSet

    class Meta:
        model = OneOnOne
        fields = [
            "id", "note", "note_meta", "member", "cycle",
            "personal_summary", "career_summary", "performance_summary", "communication_summary",
            "actions", "leader_vibe", "member_vibe", "linked_notes", "mentioned_users",
            "tags",         # input/output: flat list of IDs
            "tag_links",    # output: sectioned/grouped per 1:1 instance
            "mentioned_users", "linked_notes", "extra_notes"
        ]        
        read_only_fields = ("id", "note", "member")

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        linked_notes = validated_data.pop("linked_notes", [])
        mentioned_users = validated_data.pop("mentioned_users", [])
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
            note.mentioned_users.set(mentioned_users)
            oneonone = OneOnOne.objects.create(note=note, member=member, cycle=cycle, **validated_data)
            for tag in tags:
                OneOnOneTagLink.objects.create(one_on_one=oneonone, 
                                               tag=tag, 
                                               section=tag.section)
            grant_oneonone_access(note)
        return oneonone

    def update(self, instance, validated_data):
        """
        Update OneOnOne, Note.linked_notes, Note.mentioned_users, and TagLinks.
        Tag links are fully replaced; section always comes from tag.section.
        """
        tags = validated_data.pop("tags", None)
        linked_notes = validated_data.pop("linked_notes", None)
        mentioned_users = validated_data.pop("mentioned_users", None)

        with transaction.atomic():
            oneonone = super().update(instance, validated_data)
            note = oneonone.note

            if linked_notes is not None:
                note.linked_notes.set(linked_notes)

            if mentioned_users is not None:
                note.mentioned_users.set(list(set(mentioned_users + [oneonone.member])))

            if tags is not None:
                OneOnOneTagLink.objects.filter(one_on_one=oneonone).delete()
                for tag in tags:
                    OneOnOneTagLink.objects.create(
                        one_on_one=oneonone,
                        tag=tag,
                        section=tag.section
                    )
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