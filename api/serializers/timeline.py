from rest_framework import serializers
from rest_framework.reverse import reverse
from django.urls import NoReverseMatch

from api.models import TimelineEvent, TitleChange, Notice, StockGrant

__all__ = [
    "TimelineEventLiteSerializer",
    "TitleChangeSerializer",
    "NoticeSerializer",
    # "StockGrantSerializer",  # Disabled until stock-grant detail endpoint is finalised
]


class TimelineEventLiteSerializer(serializers.ModelSerializer):
    object_url  = serializers.SerializerMethodField()
    model       = serializers.SerializerMethodField()
    object_id   = serializers.SerializerMethodField()

    def get_object_url(self, obj):
        # Check if content_type exists before accessing its model
        if not obj.content_type:
            return None

        ct_model = obj.content_type.model

        request = self.context.get("request")

        # ──────────────────────────────────────────────
        # Front-end friendly URLs for Note/Summary
        # scheme://host/notes/<type>/<uuid>
        # ──────────────────────────────────────────────
        if ct_model in {"note", "summary"}:
            try:
                if ct_model == "note":
                    note_obj = obj.content_type.get_object_for_this_type(id=obj.object_id)
                else:  # summary ➜ fetch related note
                    summary_obj = obj.content_type.get_object_for_this_type(id=obj.object_id)
                    note_obj = summary_obj.note

                base = f"{request.scheme}://{request.get_host()}"
                return f"{base}/notes/{note_obj.type.lower()}/{note_obj.uuid}"
            except Exception:
                pass  # fall back to API URL

        # ──────────────────────────────────────────────
        # Fallback: keep old DRF reverse for other models
        # ──────────────────────────────────────────────
        viewname_map = {
            "note": "api:note-detail",
            "summary": "api:summaries-detail",
            # "stockgrant": "api:stockgrant-detail",  # Commented out - no endpoint exists
            # "notice": "api:notice-detail",  # Commented out - no endpoint exists
        }

        viewname = viewname_map.get(ct_model)
        if not viewname:
            return None

        try:
            if ct_model == "summary":
                summary_obj = obj.content_type.get_object_for_this_type(id=obj.object_id)
                return reverse(viewname, args=[summary_obj.note.id, obj.object_id], request=request)
            else:
                return reverse(viewname, args=[obj.object_id], request=request)
        except (NoReverseMatch, Exception):
            return None

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


# Simple read-only serializers for drill-down views


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "user",
            "notice_type",
            "description",
            "committee_date",
            "date_created",
        ]


# Disabled until stock-grant detail endpoint is finalised
# class StockGrantSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StockGrant
#         fields = [
#             "id",
#             "user",
#             "description",
#             "date_created",
#         ] 