from rest_framework import serializers


class UserPerformanceDataSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    name = serializers.CharField()
    last_committee_date = serializers.DateField(allow_null=True)
    committees_current_year = serializers.IntegerField(default=0)
    committees_last_year = serializers.IntegerField(default=0)
    pay_band = serializers.FloatField(allow_null=True)
    salary_change = serializers.FloatField(allow_null=True)
    is_mapped = serializers.BooleanField(default=False)
    last_bonus_date = serializers.DateField(allow_null=True)
    last_bonus_percentage = serializers.FloatField(allow_null=True)
    ladder = serializers.CharField(allow_null=True)
    ladder_levels = serializers.DictField(default=dict)
    overall_level = serializers.FloatField(allow_null=True)
    leader = serializers.CharField(allow_null=True)
    team = serializers.CharField(allow_null=True)
    tribe = serializers.CharField(allow_null=True)


class PerformanceTableResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    results = UserPerformanceDataSerializer(many=True)


__all__ = [
    "UserPerformanceDataSerializer",
    "PerformanceTableResponseSerializer",
]
