from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        write_only_fields = ['password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
