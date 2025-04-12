from django.utils import timezone
from rest_framework import serializers

from api.models import (
        Form,
        Question,
        FormAssignment,
        FormResponse,
        Cycle,
)


__all__ = ['QuestionSerializer', 'FormSerializer', 'FormDetailSerializer',
           'FormSubmissionSerializer', 'FormAssignmentSerializer', 'AggregatedResultSerializer',
           'FormResultsSerializer']


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
    assigned_by = serializers.SerializerMethodField()


    def get_is_expired(self, obj):
        if obj.is_default:
            return obj.cycle.end_date < timezone.now()
        else:
            return not FormAssignment.objects.filter(form=obj, deadline__gte=timezone.now().date()).exists()

    def get_is_filled(self, obj):
        """Returns True if the requesting user has already filled this form."""
        user = self.context['request'].user
        return FormResponse.objects.filter(form=obj, user=user).exists()

    def get_assigned_by(self, obj):
        """
        Returns a representative assigned_by id for the form.
        """
        # If the `fetch_assigned_by_forms` view method annotated the form:
        if hasattr(obj, "_assigned_by"):
            return obj._assigned_by 
        
    def get_assigned_by_name(self, obj):
        """
        Returns a representative assigned_by_name for the form.
        """
        # If the `fetch_assigned_by_forms` view method annotated the form:
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
                  'is_filled','assigned_by_name', 'assigned_by']


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
