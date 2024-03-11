from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget

from api.models import (
    Chapter,
    Committee,
    Department,
    Feedback,
    Note,
    NoteUserAccess,
    Team,
    Tribe,
    User,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("name", "date_created", "date_updated")
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


class TribeResource(resources.ModelResource):
    leader = fields.Field(
        column_name="leader",
        attribute="leader",
        widget=ForeignKeyWidget(User, field="email"),
    )
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, field="name"),
    )

    def get_instance(self, instance_loader, row):
        name = row.get("name")
        if name:
            try:
                return self._meta.model.objects.get(name=name)
            except self._meta.model.DoesNotExist:
                return None
        return None

    class Meta:
        model = Tribe
        fields = ("name", "leader", "department")


@admin.register(Tribe)
class TribeAdmin(ImportExportModelAdmin):
    resource_class = TribeResource
    date_hierarchy = "date_updated"
    list_display = (
        "name",
        "department",
        "leader",
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
    search_help_text = "جستجو در نام قبیله، نام دپارتمان، نام لیدر، ایمیل لیدر "

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


class TeamResource(resources.ModelResource):
    leader = fields.Field(
        column_name="leader",
        attribute="leader",
        widget=ForeignKeyWidget(User, field="email"),
    )
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, field="name"),
    )
    tribe = fields.Field(
        column_name="tribe",
        attribute="tribe",
        widget=ForeignKeyWidget(Tribe, field="name"),
    )

    def get_instance(self, instance_loader, row):
        name = row.get("name")
        if name:
            try:
                return self._meta.model.objects.get(name=name)
            except self._meta.model.DoesNotExist:
                return None
        return None

    class Meta:
        model = Team
        fields = ("name", "leader", "department", "tribe")


@admin.register(Team)
class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    date_hierarchy = "date_updated"
    list_display = (
        "name",
        "department",
        "leader",
        "tribe",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "name",
        ("department", "leader", "tribe"),
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


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = (
        "name",
        "date_created",
        "date_updated",
    )
    fields = (
        "uuid",
        "name",
        "description",
        "members",
        ("date_created", "date_updated"),
    )
    filter_horizontal = ("members",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام کمیته"

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


class UserResource(resources.ModelResource):
    leader = fields.Field(
        column_name="leader",
        attribute="leader",
        widget=ForeignKeyWidget(User, field="email"),
    )
    department = fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, field="name"),
    )
    team = fields.Field(
        column_name="team",
        attribute="team",
        widget=ForeignKeyWidget(Team, field="name"),
    )
    chapter = fields.Field(
        column_name="chapter",
        attribute="chapter",
        widget=ForeignKeyWidget(Chapter, field="name"),
    )

    def get_instance(self, instance_loader, row):
        email = row.get("email")
        if email:
            try:
                return self._meta.model.objects.get(email=email)
            except self._meta.model.DoesNotExist:
                return None
        return None

    class Meta:
        model = User
        fields = (
            "email",
            "name",
            "gmail",
            "phone",
            "leader",
            "department",
            "team",
            "chapter",
        )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_class = UserResource
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
        "mentioned_users",
        "summary",
        "is_public",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated", "mentioned_users")
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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = ("uuid", "owner", "note", "date_created", "date_updated")
    fields = ("uuid", ("owner", "note"), "content", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["owner__name", "owner__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

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


@admin.register(NoteUserAccess)
class NoteUserAccessAdmin(admin.ModelAdmin):
    date_hierarchy = "date_updated"
    list_display = (
        "uuid",
        "note",
        "user",
        "can_view",
        "can_edit",
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
        "can_write_summary",
        "can_write_feedback",
        "can_view_feedbacks",
        ("date_created", "date_updated"),
    )
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["user__name", "user__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

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
