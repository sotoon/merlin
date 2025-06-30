from rest_framework import serializers
from api.models.note import (
    FeedbackForm,
    FeedbackRequest,
    Feedback,
    NoteType,
    Note,
    FeedbackRequestUserLink,
)
from django.db import transaction
from django.utils import timezone
from api.models import Cycle, User
from drf_spectacular.utils import extend_schema_field


class FeedbackFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackForm
        fields = ["uuid", "title", "description", "schema"]
        read_only_fields = ["uuid"]


class FeedbackUserSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    name = serializers.CharField(read_only=True)


class FeedbackRequestUserLinkSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(source="user.uuid", read_only=True)
    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = FeedbackRequestUserLink
        fields = ("uuid", "name", "email", "answered")


class FeedbackRequestReadOnlySerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="note.title", read_only=True)
    content = serializers.CharField(source="note.content", read_only=True)
    owner_name = serializers.CharField(source="note.owner.name", read_only=True)
    owner_uuid = serializers.UUIDField(source="note.owner.uuid", read_only=True)
    date_updated = serializers.DateTimeField(source="note.date_updated", read_only=True)
    requestees = serializers.SerializerMethodField()
    form_uuid = serializers.UUIDField(
        source="form.uuid", read_only=True, allow_null=True
    )

    class Meta:
        model = FeedbackRequest
        fields = (
            "uuid",
            "title",
            "content",
            "deadline",
            "owner_name",
            "owner_uuid",
            "date_updated",
            "requestees",
            "form_uuid",
        )

    @extend_schema_field(FeedbackRequestUserLinkSerializer(many=True))
    def get_requestees(self, instance):
        request_user = self.context["request"].user
        if request_user == instance.note.owner:
            return [
                {
                    "uuid": str(link.user.uuid),
                    "name": link.user.name,
                    "email": link.user.email,
                    "answered": link.answered,
                }
                for link in instance.requestees.all()
            ]

        try:
            link = instance.requestees.get(user=request_user)
            return [
                {
                    "uuid": str(link.user.uuid),
                    "name": link.user.name,
                    "email": link.user.email,
                    "answered": link.answered,
                }
            ]
        except FeedbackRequestUserLink.DoesNotExist:
            return []


class FeedbackRequestWriteSerializer(serializers.Serializer):
    """Creates a feedback-request note and related objects in one shot."""

    title = serializers.CharField(max_length=512)
    content = serializers.CharField()
    requestee_ids = serializers.SlugRelatedField(
        many=True,
        slug_field="email",
        queryset=User.objects.all(),
        write_only=True,
        allow_empty=False,
    )
    deadline = serializers.DateField(required=False, allow_null=True)
    form_uuid = serializers.UUIDField(required=False, allow_null=True)

    def create(self, validated_data):
        owner = self.context["request"].user
        users = validated_data.pop("requestee_ids")

        deadline = validated_data.pop("deadline", None)
        if deadline and deadline < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past")

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

    def update(self, instance, validated_data):
        if instance.requestees.filter(answered=True).exists():
            raise serializers.ValidationError(
                "Cannot edit a feedback request that has already received feedback."
            )

        with transaction.atomic():
            note = instance.note
            note.title = validated_data.get("title", note.title)
            note.content = validated_data.get("content", note.content)
            note.save()

            instance.deadline = validated_data.get("deadline", instance.deadline)

            if "form_uuid" in validated_data:
                form_uuid = validated_data.get("form_uuid")
                if form_uuid:
                    try:
                        instance.form = FeedbackForm.objects.get(
                            uuid=form_uuid, is_active=True
                        )
                    except FeedbackForm.DoesNotExist:
                        raise serializers.ValidationError(
                            "Invalid or inactive feedback form"
                        )
                else:
                    instance.form = None

            instance.save()

            if "requestee_ids" in validated_data:
                new_requestees = validated_data.get("requestee_ids")
                instance.requestees.all().delete()
                from api.models.note import NoteUserAccess

                NoteUserAccess.objects.filter(note=note).exclude(
                    user=note.owner
                ).delete()

                owner = self.context["request"].user
                users = [u for u in new_requestees if u != owner]
                bulk_links = [
                    FeedbackRequestUserLink(request=instance, user=u) for u in users
                ]
                FeedbackRequestUserLink.objects.bulk_create(bulk_links)

                for u in users:
                    NoteUserAccess.objects.update_or_create(
                        user=u,
                        note=note,
                        defaults={"can_view": True},
                    )
        return instance

    def to_representation(self, instance):
        return FeedbackRequestReadOnlySerializer(instance, context=self.context).data


class FeedbackSerializer(serializers.Serializer):
    """Serializer for giving feedback (either ad-hoc or in response to request)."""

    receiver_id = serializers.UUIDField()
    feedback_request_uuid = serializers.UUIDField(required=False, allow_null=True)
    form_uuid = serializers.UUIDField(required=False, allow_null=True)
    content = serializers.CharField()
    evidence = serializers.CharField(required=False, allow_blank=True)

    uuid = serializers.UUIDField(read_only=True)
    sender = FeedbackUserSerializer(read_only=True)
    receiver = FeedbackUserSerializer(read_only=True)
    date_created = serializers.DateTimeField(read_only=True)

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
                    raise serializers.ValidationError(
                        "Invalid or inactive feedback form"
                    )
            feedback_request = None
            if feedback_request_uuid:
                feedback_request = FeedbackRequest.objects.select_related("note").get(
                    uuid=feedback_request_uuid
                )
                if receiver.id != feedback_request.note.owner_id:
                    raise serializers.ValidationError(
                        "Receiver must be the feedback-request owner"
                    )

                if (
                    feedback_request
                    and not feedback_request.requestees.filter(user=sender).exists()
                ):
                    raise serializers.ValidationError(
                        "You were not invited to answer this request"
                    )

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
            # keep the note's body in sync
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
            "sender": {"uuid": str(instance.sender.uuid), "name": instance.sender.name},
            "receiver": {
                "uuid": str(instance.receiver.uuid),
                "name": instance.receiver.name,
            },
            "date_created": instance.date_created,
        }


# ─────────────────────────────
__all__ = [
    "FeedbackFormSerializer",
    "FeedbackRequestReadOnlySerializer",
    "FeedbackRequestWriteSerializer",
    "FeedbackSerializer",
]
