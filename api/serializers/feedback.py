from rest_framework import serializers
from api.models.note import FeedbackForm, FeedbackRequest, Feedback, NoteType, Note, FeedbackRequestUserLink
from django.db import transaction
from django.utils import timezone
from api.models import Cycle, User


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
        if deadline and deadline < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past")

        form_uuid = validated_data.pop("form_uuid", None)

        users = list(User.objects.filter(uuid__in=requestee_ids))
        missing = set(requestee_ids) - {u.uuid for u in users}
        if missing:
            raise serializers.ValidationError("Some users not found")

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

            # remove requester from invitees
            users = [u for u in users if u != owner]
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
    feedback_request_uuid = serializers.UUIDField(required=False, allow_null=True)    
    form_uuid = serializers.UUIDField(required=False, allow_null=True)
    content = serializers.CharField()
    evidence = serializers.CharField(required=False, allow_blank=True)

    uuid = serializers.UUIDField(read_only=True)

    def create(self, validated_data):
        sender = self.context["request"].user
        receiver_id = validated_data.pop("receiver_id")
        feedback_request_uuid = validated_data.pop("feedback_request_uuid", None)        
        form_uuid = validated_data.pop("form_uuid", None)

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
                    try:
                        form = FeedbackForm.objects.get(uuid=form_uuid, is_active=True)
                    except FeedbackForm.DoesNotExist:
                        raise serializers.ValidationError("Invalid or inactive feedback form")
            feedback_request = None
            if feedback_request_uuid:
                feedback_request = FeedbackRequest.objects.select_related("note").get(
                    uuid=feedback_request_uuid
                )
                if receiver.id != feedback_request.note.owner_id:
                    raise serializers.ValidationError("Receiver must be the feedback-request owner")

                if feedback_request and not feedback_request.requestees.filter(user=sender).exists():
                    raise serializers.ValidationError("You were not invited to answer this request")

            # create feedback
            feedback = Feedback.objects.create(
                note=note,
                sender=sender,
                receiver=receiver,
                feedback_request=feedback_request,
                form=form,
                content=validated_data["content"],
                evidence=validated_data.get("evidence", ""),
                cycle=current_cycle,
            )

            # mark answered flag
            if feedback_request:
                FeedbackRequestUserLink.objects.filter(
                    request=feedback_request, user=sender
                ).update(answered=True)
                
            from api.models.note import NoteUserAccess
            NoteUserAccess.objects.update_or_create(
                user=receiver,
                note=note,
                defaults={"can_view": True, "can_view_feedbacks": True},
            )
        return feedback

    def update(self, instance, validated_data):
        """
        Allow the sender to edit mutable fields (content, evidence, form).
        Immutable fields — sender, receiver, feedback_request, etc. — are ignored.
        """
        if "content" in validated_data:
            instance.content = validated_data["content"]
            # keep the note’s body in sync
            instance.note.content = validated_data["content"]
            instance.note.save(update_fields=["content"])

        if "evidence" in validated_data:
            instance.evidence = validated_data["evidence"]

        if "form_uuid" in validated_data:
            form_uuid = validated_data["form_uuid"]
            try:
                instance.form = FeedbackForm.objects.get(uuid=form_uuid, is_active=True)
            except FeedbackForm.DoesNotExist:
                raise serializers.ValidationError("Invalid or inactive feedback form")

        instance.save(update_fields=["content", "evidence", "form"])
        return instance


    def validate(self, attrs):
        """
        Block self-feedback; skip the check when receiver_id is not supplied
        (e.g. partial update that only edits content).
        """
        sender = self.context["request"].user
        receiver_id = attrs.get("receiver_id")
        if receiver_id and sender.uuid == receiver_id:
            raise serializers.ValidationError("You cannot send feedback to yourself")
        return attrs

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