from django.contrib import admin

from .base import BaseModelAdmin, BaseModelResource, RESOURCE_FIELDS
from api.models import Note, Summary, Comment, NoteUserAccess


__all__ = ["NoteAdmin", "CommentAdmin", "SummaryAdmin", "NoteUserAccessAdmin"]


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    class NoteResource(BaseModelResource):
        owner = RESOURCE_FIELDS["owner"]
        mentioned_users = RESOURCE_FIELDS["mentioned_users"]
        linked_notes = RESOURCE_FIELDS["linked_notes"]
        lookup_field = "uuid"

        class Meta:
            model = Note
            fields = (
                "uuid",
                "owner",
                "title",
                "content",
                "date",
                "type",
                "proposal_type",
                "mentioned_users",
                "linked_notes",
                "cycle",
            )

    resource_class = NoteResource
    list_display = (
        "title",
        "type",
        "proposal_type",
        "owner",
        "date",
        "submit_status",
        "date_created",
        "date_updated",
    )
    list_filter = ("type", "proposal_type",)
    fields = (
        "uuid",
        ("title", "type", "proposal_type"),
        ("owner", "date", "period", "year"),
        "content",
        "mentioned_users",
        "is_public",
        "submit_status",
        "cycle",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated", "mentioned_users")
    ordering = ("-date_updated", "title")
    search_fields = [
        "uuid",
        "title",
        "owner__name",
        "owner__email",
        "cycle__name",
    ]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده، دوره عملکردی"


@admin.register(Comment)
class CommentAdmin(BaseModelAdmin):
    list_display = ("uuid", "owner", "note", "date_created", "date_updated")
    fields = (
        "uuid",
        ("owner", "note"),
        "content",
        "cycle",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = [
        "owner__name",
        "owner__email",
        "note__title",
        "cycle__name",
    ]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت، دوره عملکردی"


@admin.register(Summary)
class SummaryAdmin(BaseModelAdmin):
    class SummaryResource(BaseModelResource):
        note = RESOURCE_FIELDS["note"]

        class Meta:
            model = Summary
            fields = (
                "uuid",
                "note",
                "content",
                "performance_label",
                "ladder_change",
                "bonus",
                "salary_change",
                "committee_date",
                "cycle",
            )

    resource_class = SummaryResource
    list_display = (
        "uuid",
        "note",
        "performance_label",
        "committee_date",
        "submit_status",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "note",
        "content",
        "performance_label",
        "ladder_change",
        "bonus",
        "salary_change",
        "committee_date",
        "submit_status",
        "cycle",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = [
        "note__title",
        "note__owner__name",
        "note__owner__email",
        "cycle__name",
    ]
    search_help_text = (
        "جستجو در عنوان یادداشت، نام نویسنده، ایمیل نویسنده، دوره عملکردی"
    )


@admin.register(NoteUserAccess)
class NoteUserAccessAdmin(BaseModelAdmin):
    list_display = (
        "uuid",
        "note",
        "user",
        "can_view",
        "can_edit",
        "can_view_summary",
        "can_write_summary",
        "can_write_feedback",
        "can_view_feedbacks",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "note",
        "user",
        "can_view",
        "can_edit",
        "can_view_summary",
        "can_write_summary",
        "can_write_feedback",
        "can_view_feedbacks",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["user__name", "user__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"
