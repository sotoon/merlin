from rest_framework import serializers
from rest_framework.reverse import reverse

from api.models import TimelineEvent, TitleChange

__all__ = [
    "TimelineEventLiteSerializer",
    "TitleChangeSerializer",
]


class TimelineEventLiteSerializer(serializers.ModelSerializer):
    object_url  = serializers.SerializerMethodField()
    model       = serializers.SerializerMethodField()
    object_id   = serializers.SerializerMethodField()

    def get_object_url(self, obj):
        viewname_map = {
            "note": "api:note-detail",
            "summary": "api:summary-detail",
            "stockgrant": "api:stockgrant-detail",
            "notice": "api:notice-detail",
        }

        viewname = viewname_map.get(obj.content_type.model)
        if not viewname:
            return None

        request = self.context.get("request")
        return reverse(viewname, args=[obj.object_id], request=request)

    def get_model(self, obj):
        if obj.content_type and obj.content_type.model != "titlechange":
            return obj.content_type.model
        return None

    def get_object_id(self, obj):
        if obj.content_type and obj.content_type.model != "titlechange":
            return obj.object_id
        return None

    class Meta:
        model = TimelineEvent
        fields = [
            "id",
            "event_type",
            "effective_date",
            "summary_text",
            "object_url",
            "model",
            "object_id",
        ]


class TitleChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TitleChange
        fields = [
            "id",
            "user",
            "old_title",
            "new_title",
            "reason",
            "effective_date",
            "date_created",
        ]
        read_only_fields = ["id", "date_created"] 