from django.contrib import admin
from api.models.note import FeedbackForm, Feedback
from api.admin.base import BaseModelAdmin


@admin.register(FeedbackForm)
class FeedbackFormAdmin(BaseModelAdmin):
    list_display = ("uuid", "title", "is_active", "date_created")
    list_filter = ("is_active",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    search_fields = ("title",)


@admin.register(Feedback)
class FeedbackAdmin(BaseModelAdmin):
    list_display = ("uuid", "sender", "receiver", "date_created")
    readonly_fields = ("uuid", "date_created", "date_updated")
    search_fields = ("sender__name", "receiver__name", "content")

# Public exports for import *
__all__ = [
    "FeedbackFormAdmin",
    "FeedbackAdmin",
] 