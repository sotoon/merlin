import requests
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from api.models import User
from api.serializers import (
    TokenSerializer,
    UserSerializer,
)


__all__ = ['SignupView', 'LoginView', 'BepaCallbackView', 'VerifyTokenView']


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

