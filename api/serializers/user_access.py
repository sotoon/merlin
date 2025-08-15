from rest_framework import serializers

from api.models import User


class UserFieldSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.CharField())
    organization = serializers.CharField()

    class Meta:
        model = User
        fields = ("id", "email", "name", "roles", "organization")


class PermissionsFieldSerializer(serializers.Serializer):
    can_view_all_users = serializers.BooleanField()
    can_view_technical_users = serializers.BooleanField()
    can_view_product_users = serializers.BooleanField()
    accessible_ladders = serializers.ListField(child=serializers.CharField())
    accessible_tribes = serializers.ListField(child=serializers.CharField())
    accessible_teams = serializers.ListField(child=serializers.CharField())
    scope = serializers.CharField()


class FilterOptionsSerializer(serializers.Serializer):
    ladders = serializers.ListField(child=serializers.CharField())
    tribes = serializers.ListField(child=serializers.CharField())
    teams = serializers.ListField(child=serializers.CharField())


class UIHintsFieldSerializer(serializers.Serializer):
    show_timeline_section = serializers.BooleanField(default=True)
    show_performance_table = serializers.BooleanField(default=True)
    filter_options = FilterOptionsSerializer()


class UserPermissionsSerializer(serializers.Serializer):
    user = UserFieldSerializer()
    permissions = PermissionsFieldSerializer()
    ui_hints = UIHintsFieldSerializer()


class AccessibleUserSerializer(serializers.ModelSerializer):
    ladder = serializers.CharField(allow_null=True)
    tribe = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)

    class Meta:
        model = User
        fields = ("id", "email", "name", "ladder", "tribe", "team")


class TargetInfoSerializer(serializers.Serializer):
    ladder = serializers.CharField(allow_null=True)
    tribe = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    is_technical = serializers.BooleanField()
    is_product = serializers.BooleanField()


class TimelinePermissionsSerializer(serializers.Serializer):
    can_view = serializers.BooleanField()
    reason = serializers.CharField()
    target_info = TargetInfoSerializer()


class AccessibleUsersResponseSerializer(serializers.Serializer):
    accessible_users = AccessibleUserSerializer(many=True)
    total_count = serializers.IntegerField()
    scope = serializers.CharField()
