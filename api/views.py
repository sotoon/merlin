import requests
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from api.models import Feedback, Note, NoteType, NoteUserAccess, Summary, User
from api.permissions import FeedbackPermission, NotePermission, SummaryPermission
from api.serializers import (
    FeedbackSerializer,
    NoteSerializer,
    ProfileSerializer,
    SummarySerializer,
    TokenSerializer,
    UserSerializer,
)


class SignupView(APIView):
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    serializer_class = TokenSerializer

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
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class UsersView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

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
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        user_templates = Note.objects.filter(
            type=NoteType.Template, owner=self.request.user
        )
        public_templates = Note.objects.filter(type=NoteType.Template, is_public=True)
        return (user_templates | public_templates).distinct()


class MyTeamView(GenericAPIView):
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

    def create(self, request, *args, **kwargs):
        prev_feedback = Feedback.objects.filter(
            note=self.get_note(), owner=self.request.user
        ).first()
        if prev_feedback:
            prev_feedback.delete()
        return super().create(request, *args, **kwargs)


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
            note=current_note, user=self.request.user, can_view=True
        ).exists():
            return Summary.objects.filter(note=current_note).first()
        return Summary.objects.none()
