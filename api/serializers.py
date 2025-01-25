from rest_framework import serializers

from api.models import (
        Feedback,
        Note,
        NoteUserAccess,
        Summary,
        User,
        Form,
        Question,
        FormAssignment,
)


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

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for individual questions.
    """
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'category', 'scale_min', 'scale_max']

class FormSerializer(serializers.ModelSerializer):
    """
    Serializer for listing forms, along with its cycle metadata
    """
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    cycle_start_date = serializers.DateTimeField(source="cycle.start_date", read_only=True)
    cycle_end_date = serializers.DateTimeField(source="cycle.end_date", read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'name', 'description', 'is_default', 'form_type', 'cycle_name', 'cycle_start_date', 'cycle_end_date']

class FormDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for all questions of a form.
    """
    questions = QuestionSerializer(many=True, read_only=True, source='question_set')

    class Meta:
        model = Form
        fields = ['id', 'name', 'description', 'is_default', 'form_type', 'questions']

class FormSubmissionSerializer(serializers.Serializer):
    """
    Serializer for form submission data.
    """
    responses = serializers.DictField(
        child=serializers.IntegerField(allow_null=True),
        required=True
    )

class FormAssignmentSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source="form.name", read_only=True)

    class Meta:
        model = FormAssignment
        fields = ["form_name", "assigned_to", "deadline", "is_completed"]