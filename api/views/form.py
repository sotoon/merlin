import copy
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, time
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import User, Form, Question, FormResponse, FormAssignment, Cycle
from api.utils import calculate_form_results
from api.serializers import (
    FormSerializer,
    FormDetailSerializer,
    FormSubmissionSerializer,
    FormResultsSerializer,
)
from api.views.mixins import CycleQueryParamMixin


__all__ = ['FormViewSet']


class FormViewSet(CycleQueryParamMixin, viewsets.ModelViewSet):
    """
    A ViewSet to handle CRUD operations on forms, and form assignment.
    """
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]  # FUTURE ENHANCEMENT: Add FormPermission

    def list(self, request):
        """
        Override the default list to include default and assigned forms.
        - Default forms available to everyone. (based on active cycle)
        - Forms assigned specifically to the user. (with custom deadlines)

        Return a list of active and expired forms assigned to the user.
        """
        user = request.user

        # fetch default and manually assigned forms, separately
        # NOTE: Alternative Method: Sending all forms and put the separation queries in the front side.

        # default_forms = Form.objects.filter(is_default=True, cycle__is_active=True)
        assigned_forms = Form.objects.filter(formassignment__assigned_to=user)

        # all_forms = (default_forms | assigned_forms).distinct()
        all_forms = assigned_forms

        active_forms = []
        expired_forms = []

        for form in all_forms:
            if form.is_default:
                # Default forms: Use the cycle and end date to determine expiration
                if form.cycle.end_date >= timezone.now():
                    active_forms.append(form)
                else:
                    expired_forms.append(form)
            else:
                # Non-default forms: Use the assignment's deadline to determine expiration
                if FormAssignment.objects.filter(form=form, assigned_to=user, deadline__gte=timezone.now().date()).exists():
                    active_forms.append(form)
                else:
                    expired_forms.append(form)

        return Response({
            "active_forms": FormSerializer(active_forms, many=True, context={"request": request}).data,
            "expired_forms": FormSerializer(expired_forms, many=True, context={"request": request}).data,
        })
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific form and its questions.
        """
        form = get_object_or_404(Form,id=pk)

        serializer = FormDetailSerializer(form, context={"request": request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        Handle form submission. Saves responses for each question and marks the assignment as completed.

        For default forms:
        - Set `assigned_by` to the leader for TL forms.
        """
        # Fetch the form and all of its questions
        form = get_object_or_404(Form, id=pk)

        # Check if the user has already submitted this form
        if FormResponse.objects.filter(form=form, user=request.user).exists():
            return Response(
                {"detail": "You have already submitted this form."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
        # Check if form is default and active
        if form.is_default and not form.cycle.is_active:
            return Response({"detail": "This form is not active."}, status=400)
        
        # Validate deadline for assigned forms
        assignment = FormAssignment.objects.filter(form=form, assigned_to=request.user).first()
        if assignment and assignment.deadline < timezone.now().date():
            return Response({"detail": "Submission deadline has passed."}, status=400)

        # Validate TL forms require leaders
        if form.form_type == Form.FormType.TL and not request.user.get_leaders():
            return Response(
                {"detail": "Cannot submit this form. No leader assigned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        questions = Question.objects.filter(form=form)
    
        # Validate the incoming request
        serializer = FormSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        responses = serializer.validated_data.get("responses", {})

        for question in questions:
            question_key = f"question_{question.id}" if question else None
            # Check if an answer exists for this question; if not, use `None`
            answer = responses.get(question_key, None) if question else None

            # Save the response for this question in the FormResponse table
            FormResponse.objects.create(
                user=request.user,
                form=form,
                question=question,
                answer=answer,
            )
            
        # Update assigned_by for default forms
        if form.is_default and not assignment:
            assigned_by = request.user.get_leaders() if form.form_type == Form.FormType.TL else None
            assignment = FormAssignment.objects.create(
                form=form,
                assigned_to=request.user,
                assigned_by=assigned_by,
                deadline=form.cycle.end_date,
            )

        # Update the FormAssignment status if applicable
        if assignment:
            assignment.is_completed=True 
            assignment.save()

        return Response({"status": "Form submitted successfully"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='assign')
    def assign(self, request):
        """
        Assign a form to a specific user with an optional message.
        - Ensure that the form is visible to the assignee.
        - Prevents duplicate assignments.
        
        For default forms, this is managed automatically through signals.
        """

        form_id = request.data.get("form_id")
        assigned_to_id = request.data.get("assigned_to")
        message = request.data.get("message", "")
        deadline = request.data.get("deadline")

        # Validate that the form and the user exist
        form = get_object_or_404(Form, id=form_id)
        assigned_to = get_object_or_404(User, id=assigned_to_id)

        if form.is_default:
            return Response(
                {"detail": "Default forms cannot be assigned manually."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Assign, prevent duplication
        assignment, created = FormAssignment.objects.get_or_create(
            form=form,
            assigned_to=assigned_to,
            assigned_by=request.user,
            message=message,
            defaults={"message":message, "deadline":deadline},
        )

        if not created:
            return Response(
                {"detail": "This form has already been assigned to this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        return Response({"status": "Form assigned successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="results")
    def results(self, request, pk=None):
        """
        Fetch aggregated results for a form.
        Returns a structured JSON with:
          - "my_results": aggregated results for the current user (if they are the assessed user)
          - "team_results": a list of aggregated results for each subordinate (if any)
        Availability conditions:
          - Default forms: results are shown only if the cycle has ended.
          - Manual forms: results are shown only if the assignment deadline(s) have passed.
        """
        form = self.get_object()
        cycle_id = request.query_params.get("cycle_id")

        # Validate cycle existence
        if cycle_id:
            cycle = get_object_or_404(Cycle, id=cycle_id)
        else:
            # Fetch the latest cycle if `cycle_id` is missing               FUTURE ENHANCEMENT: this will not support simultaneous cycles
            cycle = Cycle.objects.order_by("-end_date").first()

        if not cycle:
            return Response(
                {"detail": "No valid cycle found to fetch results."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        now = timezone.now()
        # Handle default forms
        if form.is_default:
            if cycle.end_date > now:
                return Response(
                    {"detail": "Results for this form are not available until the cycle ends."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # For default forms, use all assignments (no deadline filtering)
            my_assignments = form.formassignment_set.filter(assigned_by=request.user)
            team_assignments = form.formassignment_set.filter(assigned_by__leader=request.user)
            
            if not my_assignments.exists() and not team_assignments.exists():
                return Response(
                    {"detail": "You are not authorized to view results for this form."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        # Handle non-default forms
        else:
            # For manual forms, only include assignments whose deadline has passed
            today = now.date()
            my_assignments = form.formassignment_set.filter(
                assigned_by=request.user,
                deadline__lte=today
            )
            team_assignments = form.formassignment_set.filter(
                assigned_by__leader=request.user,
                deadline__lte=today
            )
            if not my_assignments.exists() and not team_assignments.exists():
                return Response(
                    {"detail": "Results for this form are not available until the deadline passes."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Check permissions: if no assignments exist for current user or their subordinates, deny access.
        if not my_assignments.exists() and not team_assignments.exists():
            return Response(
                {"detail": "You are not authorized to view results for this form."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Adjust the cycle's end date to include the entire day
        adjusted_end_date = timezone.make_aware(datetime.combine(cycle.end_date, time.max))

        # A helper to fetch and calculate results given a queryset of assignments
        def get_aggregated_results(assignments):
            # If there are no assignments, return None
            if not assignments.exists():
                return None
            # We want to group by the assessed user (assigned_by).
            aggregated_list = []
            distinct_assessed_ids = assignments.values_list("assigned_by", flat=True).distinct()
            for assessed_id in distinct_assessed_ids:
                # Get assignments for this assessed user
                assignments_for_assessed = assignments.filter(assigned_by=assessed_id)
                responses = FormResponse.objects.filter(
                    question__form=form,
                    user__in=assignments_for_assessed.values_list("assigned_to", flat=True),
                    date_created__range=(cycle.start_date, adjusted_end_date),
                )
                aggregated = calculate_form_results(responses, form)
                # Add the assessed user's id and name
                aggregated["assigned_by"] = assessed_id
                try:
                    user_obj = User.objects.get(id=assessed_id)
                    aggregated["assigned_by_name"] = user_obj.name
                except User.DoesNotExist:
                    aggregated["assigned_by_name"] = ""
                aggregated_list.append(aggregated)

            return aggregated_list

        # Get results for the current user (My Results)
        my_results_data = get_aggregated_results(my_assignments)
        # Since the current user is the assessed user, we expect a single aggregated result.
        my_results = my_results_data if my_results_data else []
        # Get results for the team (My Team's Results)
        team_results = get_aggregated_results(team_assignments) or []

        # Prepare the structured response
        response_data = {
            "my_results": my_results,
            "team_results": team_results,
        }

        serializer = FormResultsSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="assigned-by")
    def fetch_assigned_by_forms(self, request):
        """
        Returns a structured JSON object with two keys:
        - "my_forms": forms where the current user is directly the assessed user (assigned_by == request.user)
        - "team_forms": forms where the current user is the leader of an assessed user (assigned_by__leader == request.user)
        Optionally filters by cycle (using cycle_id). If omitted, uses the latest cycle.
        Each form is serialized using FormSerializer.
        """
        cycle_id = request.query_params.get("cycle_id")
        if cycle_id:
            cycle = get_object_or_404(Cycle, id=cycle_id)
        else:
            cycle = Cycle.objects.order_by("-end_date").first()
            if not cycle:
                return Response({"detail": "No valid cycle found."}, status=status.HTTP_400_BAD_REQUEST)
        
        forms = Form.objects.filter(cycle=cycle)
        # my_forms: forms where an assignment exists with assigned_by == request.user.
        my_forms = forms.filter(formassignment__assigned_by=request.user).distinct()
        
        # Annotate each form with a custom attribute for assigned_by_name.
        for form in my_forms:
            form._assigned_by_name = request.user.name
            form._assigned_by = request.user.id
        
        # team_forms: forms where an assignment exists with assigned_by__leader == request.user,
        team_assignments = FormAssignment.objects.filter(form__cycle=cycle, assigned_by__leader=request.user)
        # Group by form and assessed user.
        distinct_pairs = team_assignments.values_list("form_id", "assigned_by", flat=False).distinct()

        team_forms = []
        for form_id, assessed_id in distinct_pairs:
            form = Form.objects.get(id=form_id)

            try:
                assigned_by_name = User.objects.get(id=assessed_id).name
            except User.DoesNotExist:
                assigned_by_name = ""
            # Shallow-copy the form so that each entry is independent.
            form_copy = copy.copy(form) 
            form_copy._assigned_by = assessed_id
            form_copy._assigned_by_name = assigned_by_name
            team_forms.append(form_copy)
                
        my_serializer = FormSerializer(my_forms, many=True, context={"request": request})
        team_serializer = FormSerializer(team_forms, many=True, context={"request": request})

        return Response({
            "my_forms": my_serializer.data,
            "team_forms": team_serializer.data
        })
