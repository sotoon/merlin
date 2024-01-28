from django.contrib import admin

from api.models import Chapter, Department, Note, Team, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("name", "description", "date_created", "date_updated")
    fields = ("uuid", "name", "description", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام دپارتمان"

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


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
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام چپتر، نام دپارتمان، نام لیدر، ایمیل لیدر "

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


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
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام تیم، نام دپارتمان، نام لیدر، ایمیل لیدر "

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = (
        "email",
        "name",
        "phone",
        "department",
        "chapter",
        "team",
        "leader",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "name",
        "phone",
        ("email", "gmail"),
        ("department", "chapter", "team", "leader"),
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "email")
    search_fields = ["email", "name", "phone"]
    search_help_text = "جستجو در نام کاربر، ایمیل، موبایل"

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("title", "type", "owner", "date", "date_created", "date_updated")
    fields = (
        "uuid",
        ("title", "type"),
        ("owner", "date"),
        "content",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_updated", "title")
    search_fields = ["title", "owner__name", "owner__email"]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده"

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
