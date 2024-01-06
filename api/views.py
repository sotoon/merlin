from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from api.serializers import UserSerializer

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            data = {
                'username': user.username,
                'email': user.email,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username_or_email = request.data.get('username_or_email')
        password = request.data.get('password')

        if '@' in username_or_email:
            kwargs = {'email': username_or_email}
        else:
            kwargs = {'username': username_or_email}

        user = User.objects.filter(**kwargs).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            data = {
                'username': user.username,
                'email': user.email,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
