import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from api.models import Feedback, Note, NoteType, User
from api.serializers import (
    FeedbackSerializer,
    NoteSerializer,
    ProfileSerializer,
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
    permission_classes = [IsAuthenticated]
    search_fields = ["type"]

    def get_object(self):
        uuid = self.kwargs["uuid"]
        note = get_object_or_404(Note, uuid=uuid)
        current_user = self.request.user
        if (
            note.owner == current_user
            or (note.owner.leader == current_user and note.type != NoteType.Personal)
            or (current_user in note.mentioned_users.all())
        ):
            return note
        raise PermissionDenied("You don't have permission to access this note.")

    def update(self, request, *args, **kwargs):
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("You don't have permission to update this note.")
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user_email = self.request.query_params.get("user")
        retrieve_mentions = self.request.query_params.get("retrieve_mentions")
        if user_email:
            notes_owner = User.objects.get(email=user_email)
            if notes_owner.leader != self.request.user:
                raise PermissionDenied("You don't have permission to access this note.")
            queryset = (
                Note.objects.filter(owner=notes_owner)
                .exclude(type=NoteType.Personal)
                .distinct()
            )
        else:
            if retrieve_mentions:
                queryset = Note.objects.filter(
                    mentioned_users=self.request.user
                ).distinct()
            else:
                queryset = Note.objects.filter(owner=self.request.user).distinct()
        type = self.request.query_params.get("type")
        if type:
            queryset = queryset.filter(type=type)
        return queryset


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
    permission_classes = [IsAuthenticated]

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
        feedback = get_object_or_404(Feedback, uuid=uuid)
        current_user = self.request.user
        if feedback.note == self.get_note() and feedback.note.owner == current_user:
            return feedback
        raise PermissionDenied("You don't have permission to access this feedback.")

    def get_queryset(self):
        if self.request.user != self.get_note().owner:
            return Feedback.objects.filter(
                note=self.get_note(), owner=self.request.user
            )
        return Feedback.objects.filter(note=self.get_note())

    def create(self, request, *args, **kwargs):
        current_user = self.request.user
        if (
            self.get_note().owner.leader != current_user
            and current_user not in self.get_note().mentioned_users.all()
        ):
            raise PermissionDenied("You don't have permission to create feedback.")
        prev_feedback = Feedback.objects.filter(
            note=self.get_note(), owner=current_user
        ).first()
        if prev_feedback:
            prev_feedback.delete()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("You don't have permission to update this feedback.")
        return super().update(request, *args, **kwargs)
