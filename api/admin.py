from django.contrib import admin

from api.models import Chapter, Department, Note, Team


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("name", "description", "date_created", "date_updated")
    fields = ("uuid", "name", "description", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام دپارتمان"


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = (
        "name",
        "department",
        "leader",
        "description",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "name",
        ("department", "leader"),
        "description",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__username", "leader__email"]
    search_help_text = "جستجو در نام چپتر، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = (
        "name",
        "department",
        "leader",
        "description",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "name",
        ("department", "leader"),
        "description",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__username", "leader__email"]
    search_help_text = "جستجو در نام تیم، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("title", "type", "owner", "date", "date_created", "date_updated")
    fields = (
        "uuid",
        "title",
        ("owner", "date"),
        "content",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_updated", "title")
    search_fields = ["title", "owner__username", "owner__email"]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده"
