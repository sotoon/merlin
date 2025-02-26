from django.utils import timezone
from rest_framework import serializers
from django.db.models import Q

from api.models import (
        Feedback,
        Note,
        NoteUserAccess,
        Summary,
        User,
        Form,
        Question,
        FormAssignment,
        FormResponse,
        Cycle,
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

    def to_representation(self, instance):
        data = super(NoteSerializer, self).to_representation(instance)
        data['submit_status'] = data.pop('submit_status_name')
        return data

class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for individual questions.
    """
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'category', 'scale_min', 'scale_max']

class FormSerializer(serializers.ModelSerializer):
    """
    Serializer for listing forms, along with its cycle metadata,
    and assignment completion status.
    """
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    cycle_start_date = serializers.DateTimeField(source="cycle.start_date", read_only=True)
    cycle_end_date = serializers.DateTimeField(source="cycle.end_date", read_only=True)
    cycle = serializers.PrimaryKeyRelatedField(queryset=Cycle.objects.all())
    is_expired = serializers.SerializerMethodField()
    is_filled = serializers.SerializerMethodField()
    assigned_by_name = serializers.SerializerMethodField()

    def get_is_expired(self, obj):
        if obj.is_default:
            return obj.cycle.end_date < timezone.now()
        else:
            return not FormAssignment.objects.filter(form=obj, deadline__gte=timezone.now().date()).exists()

    def get_is_filled(self, obj):
        """Returns True if the requesting user has already filled this form."""
        user = self.context['request'].user
        return FormResponse.objects.filter(form=obj, user=user).exists()

    def get_assigned_by_name(self, obj):
        """
        Returns a representative assigned_by_name for the form.
        """
        # If the `fetch_assigned_by_forms`` view method annotated the form:
        if hasattr(obj, "_assigned_by_name"):
            return obj._assigned_by_name
        
        # Fallback:                                 # FUTURE ENHANCEMENT: Maybe better to be removed
        request = self.context.get("request")
        if request:
            user = request.user
            assignment = obj.formassignment_set.filter(assigned_by__leader=user).order_by('id').first()
            if assignment and assignment.assigned_by:
                return assignment.assigned_by.name
            assignment = obj.formassignment_set.filter(assigned_by=user).order_by('id').first()
            if assignment and assignment.assigned_by:
                return assignment.assigned_by.name
        return ""

    class Meta:
        model = Form
        fields = ['id', 'name', 'description', 'is_default', 'form_type', 'cycle',
                  'cycle_name', 'cycle_start_date', 'cycle_end_date', 'is_expired',
                  'is_filled','assigned_by_name']

class FormDetailSerializer(FormSerializer):
    """
    Serializer for all questions of a form.
    """
    questions = QuestionSerializer(many=True, read_only=True, source='question_set')
    previous_responses = serializers.SerializerMethodField()
    assigned_by = serializers.SerializerMethodField()

    def get_previous_responses(self, obj):
        """Fetch previous responses of the requesting user for this form."""
        user = self.context["request"].user
        responses = FormResponse.objects.filter(form=obj, user=user)
        return {f"question_{r.question.id}": r.answer for r in responses}

    def get_assigned_by(self, obj):
        """Fetch the assigned_by as the assessed user."""
        user = self.context["request"].user
        assignment = FormAssignment.objects.filter(form=obj, assigned_to=user).first()
        return assignment.assigned_by.name if assignment and assignment.assigned_by else None

    class Meta(FormSerializer.Meta):
        model = Form
        fields = FormSerializer.Meta.fields + ['questions', 'previous_responses', 'assigned_by']

class FormSubmissionSerializer(serializers.Serializer):
    """
    Serializer for form submission data.
    """
    responses = serializers.DictField(
        child=serializers.IntegerField(allow_null=True),
        required=True
    )

class FormAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for assigning forms.
    """
    form_name = serializers.CharField(source="form.name", read_only=True)

    class Meta:
        model = FormAssignment
        fields = ["form_name", "assigned_to", "deadline", "is_completed"]

class AggregatedResultSerializer(serializers.Serializer):
    assigned_by = serializers.IntegerField()
    assigned_by_name = serializers.CharField()
    total_average = serializers.FloatField(allow_null=True)
    categories = serializers.DictField(child=serializers.FloatField())
    questions = serializers.ListField(child=serializers.DictField())

class FormResultsSerializer(serializers.Serializer):
    my_results = AggregatedResultSerializer(many=True)
    team_results = AggregatedResultSerializer(many=True)