from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import User
from api.serializers import (
    ProfileSerializer,
    ProfileListSerializer,
)


__all__ = ['ProfileView', 'UsersView', 'MyTeamView']


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

