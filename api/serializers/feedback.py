from rest_framework import serializers
from api.models.note import FeedbackForm, FeedbackRequest, Feedback, NoteType, Note, FeedbackRequestUserLink
from django.db import transaction
from django.utils import timezone
from api.models.cycle import Cycle


class FeedbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = ["uuid", "title", "description", "schema"]
        read_only_fields = ["uuid"]


class FeedbackRequestSerializer(serializers.Serializer):
    """Creates a feedback-request note and related objects in one shot."""

    title = serializers.CharField(max_length=512)
    content = serializers.CharField()
    requestee_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, allow_empty=False
    )
    deadline = serializers.DateField(required=False, allow_null=True)
    form_uuid = serializers.UUIDField(required=False, allow_null=True)

    uuid = serializers.UUIDField(read_only=True)

    def create(self, validated_data):
        owner = self.context["request"].user
        requestee_ids = validated_data.pop("requestee_ids")
        deadline = validated_data.pop("deadline", None)
        form_uuid = validated_data.pop("form_uuid", None)
        with transaction.atomic():
            current_cycle = Cycle.get_current_cycle()
            if current_cycle is None:
                raise serializers.ValidationError("No active cycle defined")

            note = Note.objects.create(
                owner=owner,
                title=validated_data["title"],
                content=validated_data["content"],
                date=timezone.now().date(),
                type=NoteType.FEEDBACK_REQUEST,
                cycle=current_cycle,
            )
            fform = None
            if form_uuid:
                try:
                    fform = FeedbackForm.objects.get(uuid=form_uuid, is_active=True)
                except FeedbackForm.DoesNotExist:
                    raise serializers.ValidationError("Invalid form selected")
            frequest = FeedbackRequest.objects.create(
                note=note, deadline=deadline, form=fform
            )
            # Link requestees
            from api.models import User
            users = User.objects.filter(uuid__in=requestee_ids)
            bulk_links = [
                FeedbackRequestUserLink(request=frequest, user=u) for u in users
            ]
            FeedbackRequestUserLink.objects.bulk_create(bulk_links)

            # ACL: invitees can view the request note
            from api.models.note import NoteUserAccess
            for u in users:
                NoteUserAccess.objects.update_or_create(
                    user=u,
                    note=note,
                    defaults={"can_view": True},
                )
        return frequest

    def to_representation(self, instance):
        return {
            "uuid": instance.uuid,
            "title": instance.note.title,
            "content": instance.note.content,
            "deadline": instance.deadline,
            "requestees": [
                {"uuid": link.user.uuid, "name": link.user.name, "answered": link.answered}
                for link in instance.requestees.select_related("user")
            ],
        }


class FeedbackSerializer(serializers.Serializer):
    """Serializer for giving feedback (either ad-hoc or in response to request)."""

    receiver_id = serializers.UUIDField()
    request_note_uuid = serializers.UUIDField(required=False, allow_null=True)
    form_uuid = serializers.UUIDField(required=False, allow_null=True)
    content = serializers.CharField()
    evidence = serializers.CharField(required=False, allow_blank=True)

    uuid = serializers.UUIDField(read_only=True)

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver_id = validated_data.pop("receiver_id")
        request_note_uuid = validated_data.pop("request_note_uuid", None)
        form_uuid = validated_data.pop("form_uuid", None)
        from api.models import User
        receiver = User.objects.get(uuid=receiver_id)
        with transaction.atomic():
            current_cycle = Cycle.get_current_cycle()
            if current_cycle is None:
                raise serializers.ValidationError("No active cycle defined")

            note = Note.objects.create(
                owner=sender,
                title=f"Feedback from {sender.name}",
                content=validated_data["content"],
                date=timezone.now().date(),
                type=NoteType.FEEDBACK,
                cycle=current_cycle,
            )
            form = None
            if form_uuid:
                form = FeedbackForm.objects.get(uuid=form_uuid, is_active=True)
            request_note = None
            if request_note_uuid:
                request_note = Note.objects.get(uuid=request_note_uuid)
            feedback = Feedback.objects.create(
                note=note,
                sender=sender,
                receiver=receiver,
                request_note=request_note,
                form=form,
                content=validated_data["content"],
                evidence=validated_data.get("evidence", ""),
                cycle=current_cycle,
            )
            # TODO: grant access to receiver & sender (by default owner has)
            from api.models.note import NoteUserAccess
            NoteUserAccess.objects.update_or_create(
                user=receiver,
                note=note,
                defaults={"can_view": True, "can_view_feedbacks": True},
            )
        return feedback

    def to_representation(self, instance):
        return {
            "uuid": instance.uuid,
            "content": instance.content,
            "evidence": instance.evidence,
            "sender": {"uuid": instance.sender.uuid, "name": instance.sender.name},
            "receiver": {"uuid": instance.receiver.uuid, "name": instance.receiver.name},
            "date_created": instance.date_created,
        }

# ─────────────────────────────
__all__ = [
    "FeedbackFormSerializer",
    "FeedbackRequestSerializer",
    "FeedbackSerializer",
] 