from rest_framework import serializers


__all__ = ['TokenSerializer']


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()

