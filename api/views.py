import requests
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from api.models import Feedback, Note, NoteType, NoteUserAccess, Summary, User, Form, Question, FormResponse, FormAssignment, Cycle
from api.permissions import FeedbackPermission, NotePermission, SummaryPermission
from api.serializers import (
    FeedbackSerializer,
    NoteSerializer,
    ProfileSerializer,
    ProfileListSerializer,
    SummarySerializer,
    TokenSerializer,
    UserSerializer,
    FormSerializer,
    FormDetailSerializer,
    FormSubmissionSerializer,
    FormResultsSerializer,
)

AUTH_RESPONSE_SCHEMA = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "name": openapi.Schema(
            type=openapi.TYPE_STRING, description="Name of the user"
        ),
        "email": openapi.Schema(
            type=openapi.TYPE_STRING, description="Email of the user"
        ),
        "tokens": openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh token",
                ),
                "access": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Access token"
                ),
            },
        ),
    },
)


class SignupView(APIView):
    """
    API endpoint for creating a new user.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Response(
                "Successfully Signed Up!",
                schema=AUTH_RESPONSE_SCHEMA,
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            refresh["name"] = user.name
            refresh["email"] = user.email
            data = {
                "name": user.name,
                "email": user.email,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API endpoint for logging in a user.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: openapi.Response(
                "Successfully Logged In!",
                schema=AUTH_RESPONSE_SCHEMA,
            )
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            refresh["name"] = user.name
            refresh["email"] = user.email
            data = {
                "name": user.name,
                "email": user.email,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
            return Response(data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class BepaCallbackView(APIView):
    """
    Gets the code from the BEPA and exchanges it for an access token.
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "code",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Code from BEPA",
            )
        ],
        responses={
            200: openapi.Response(
                "Successfully Logged In!",
                schema=AUTH_RESPONSE_SCHEMA,
            )
        },
    )
    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code")
        if not code:
            return Response(
                {"error": "Code not provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Exchange code for token
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": settings.BEPA_CLIENT_ID,
            "client_secret": settings.BEPA_CLIENT_SECRET,
            "redirect_uri": settings.BEPA_REDIRECT_URI,
        }
        token_request_headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = requests.post(
            settings.BEPA_TOKEN_URL, data=token_data, headers=token_request_headers
        )
        token_json = token_response.json()

        if "error" in token_json:
            return Response(token_json, status=status.HTTP_400_BAD_REQUEST)

        access_token = token_json["access_token"]
        user_info_response = requests.get(
            settings.BEPA_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_info_response.json()

        name = user_info.get("name")
        email = user_info.get("email")

        user, created = User.objects.get_or_create(email=email)

        if not user.name:
            user.name = name
            user.save()

        if created:
            user.set_unusable_password()
            user.save()

        refresh = RefreshToken.for_user(user)
        refresh["name"] = user.name
        refresh["email"] = user.email
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(data, status=status.HTTP_200_OK)


class VerifyTokenView(GenericAPIView):
    """
    Gets a token and validates it and returns user data
    """

    serializer_class = TokenSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "token",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Token",
            )
        ],
        responses={
            200: openapi.Response(
                description="Verified Successfully", schema=UserSerializer
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        try:
            valid_data = AccessToken(token)
            user_id = valid_data["user_id"]
            user = User.objects.get(id=user_id)
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileView(RetrieveUpdateAPIView):
    """
    Update or read Profile data
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UsersView(ListAPIView):
    """
    List all app users
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileListSerializer

    def get_queryset(self):
        return User.objects.all()


class NoteViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = NoteSerializer
    permission_classes = (IsAuthenticated, NotePermission)
    search_fields = ["type"]

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Note, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        user_email = self.request.query_params.get("user")
        retrieve_mentions = self.request.query_params.get("retrieve_mentions")
        accessible_note_ids = NoteUserAccess.objects.filter(
            user=self.request.user, can_view=True
        ).values_list("note__uuid", flat=True)
        accessible_notes = Note.objects.filter(uuid__in=accessible_note_ids)
        if user_email:
            queryset = accessible_notes.filter(owner__email=user_email)
        elif retrieve_mentions:
            queryset = accessible_notes.filter(~Q(owner=self.request.user))
        else:
            queryset = accessible_notes.filter(owner=self.request.user)
        type = self.request.query_params.get("type")
        if type:
            queryset = queryset.filter(type=type)
        return queryset.distinct()

    @action(detail=True, methods=["post"], url_path="read")
    def mark_note_as_read(self, request, uuid=None):
        """
        Mark note as read(Does not need any input params)
        """
        note = self.get_object()
        user = request.user
        if user not in note.read_by.all():
            note.read_by.add(user)
            return Response(
                {"status": "Note marked as read for the current user."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "Note is already marked as read for the current user."},
                status=status.HTTP_200_OK,
            )

    @action(detail=True, methods=["post"], url_path="unread")
    def mark_note_as_unread(self, request, uuid=None):
        """
        Mark note as unread(Does not need any input params)
        """
        note = self.get_object()
        user = request.user
        if user in note.read_by.all():
            note.read_by.remove(user)
            return Response(
                {"status": "Note marked as unread for the current user."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "Note is already marked as unread for the current user."},
                status=status.HTTP_200_OK,
            )


class TemplatesView(ListAPIView):
    """
    List available templates
    """

    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        user_templates = Note.objects.filter(
            type=NoteType.Template, owner=self.request.user
        )
        public_templates = Note.objects.filter(type=NoteType.Template, is_public=True)
        return (user_templates | public_templates).distinct()


class MyTeamView(GenericAPIView):
    """
    List users that the current user lead
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        team_users = User.objects.filter(leader=user)
        serializer = self.get_serializer(team_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedbackViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, FeedbackPermission]
    search_fields = ["owner"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"note_uuid": self.kwargs.get("note_uuid", None)})
        return context

    def get_note(self):
        return get_object_or_404(
            Note,
            uuid=self.kwargs["note_uuid"],
        )

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Feedback, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        current_note = self.get_note()
        all_note_feedbacks = Feedback.objects.filter(note=current_note).distinct()
        owner_email = self.request.query_params.get("owner")
        if owner_email:
            all_note_feedbacks = all_note_feedbacks.filter(owner__email=owner_email)
        if NoteUserAccess.objects.filter(
            note=current_note, user=self.request.user, can_view_feedbacks=True
        ).exists():
            return all_note_feedbacks
        return all_note_feedbacks.filter(owner=self.request.user)


class SummaryViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated, SummaryPermission]
    search_fields = ["owner"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"note_uuid": self.kwargs.get("note_uuid", None)})
        return context

    def get_note(self):
        return get_object_or_404(
            Note,
            uuid=self.kwargs["note_uuid"],
        )

    def get_object(self):
        uuid = self.kwargs["uuid"]
        obj = get_object_or_404(Summary, uuid=uuid)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        current_note = self.get_note()
        if NoteUserAccess.objects.filter(
            note=current_note, user=self.request.user, can_view_summary=True
        ).exists():
            return Summary.objects.filter(note=current_note)
        return Summary.objects.none()

class FormViewSet(viewsets.ModelViewSet):
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
        - Forms assigned specifically to the user. (with costum deadlines)
        """

        user = request.user

        # fetch default and manually assigned forms, separately
        # NOTE: Alternative Method: Sending all forms and put the separation queries there.

        default_forms = Form.objects.filter(is_default=True, cycle__is_active=True)
        assigned_forms = Form.objects.filter(formassignment__assigned_to=user)

        all_forms = (default_forms | assigned_forms).distinct()

        serializer = FormSerializer(all_forms, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific form and its questions.
        """
        form = get_object_or_404(Form,id=pk)

        serializer = FormDetailSerializer(form)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        Handle form submission. Saves responses for each question and marks the assignment as completed.
        """
        # Fetch the form and all of its questions
        form = get_object_or_404(Form, id=pk)

         # Check if the user has already submitted this form
        if FormResponse.objects.filter(form=form, user=request.user).exists():
            return Response(
                {"detail": "You have already submitted this form."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    
        # Check if for is default and its cycle is active
        if form.is_default and not form.cycle.is_active:
            return Response({"detail": "This form is not active."}, status=400)
        
        # Validate deadline for assigned forms
        assignment = FormAssignment.objects.filter(form=form, assigned_to=request.user).first()
        if assignment and assignment.deadline < timezone.now():
            return Response({"detail": "Submission deadline has passed."}, status=400)

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
        
        # Update the FormAssignment status if applicable
        assignment = FormAssignment.objects.filter(form=form, assigned_to=request.user).first()
        if assignment:
            assignment.is_completed=True 
            assignment.save()

        return Response({"status": "Form submitted successfully"}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='assign')
    def assign(self, request):
        """
        Assign a form to a specific user with an optional message.
        - Ensure thath the form is visible to the assignee.
        - Prevents duplicate assignments.
        """

        form_id = request.data.get("form_id")
        assigned_to_id = request.data.get("assigned_to")
        message = request.data.get("message", "")
        deadline = request.data.get("deadline")

        # Validate that the form and the user exist
        form = get_object_or_404(Form, id=form_id)
        assigned_to = get_object_or_404(User, id=assigned_to_id)

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
        Results are only shown if:
        - The cycle (for default forms) has ended.
        - The deadline (for assigned forms) has passed.
        """
        form = self.get_object()
        cycle_id = request.query_params.get("cycle_id") # Should be sent by client side

        if cycle_id:
            cycle = get_object_or_404(Cycle, id=cycle_id)

            if cycle.end_date > timezone.now().date():
                return Response(
                    {"detail": "Results for this form are not available until the cycle ends."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            # Fetch responses within the cycle date range
            responses = FormResponse.objects.filter(
                question__form=form,
                created_at__range=(cycle.start_date, cycle.end_date)
            )

        # Handle manually assigned forms
        else:
            assignments = FormAssignment.objects.filter(form=form, assigned_to=request.user)

            # Validate that all deadlines have passed
            for assignment in assignments:
                if assignment.deadline and assignment.deadline > timezone.now():
                    return Response(
                        {"detail": "Results for this form are not available until the deadline passes."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Fetch responses for the assigned users
            responses = FormResponse.objects.filter(
                question__form=form,
                user__in=assignments.values_list("assigned_to", flat=True)
            )

        # Calculate aggregated results
        results = calculate_form_results(responses, form)
        serializer = FormResultsSerializer(results)
        return Response(serializer.data)