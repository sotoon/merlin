# flake8: noqa: E501
from django.contrib import admin
from import_export import fields, resources
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

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


# fmt: off
class BaseModelAdmin(ImportExportModelAdmin):
    date_hierarchy = "date_updated"

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


RESOURCE_FIELDS = {
    "leader": fields.Field(
        column_name="leader",
        attribute="leader",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "owner": fields.Field(
        column_name="owner",
        attribute="owner",
        widget=ForeignKeyWidget(User, field="name"),
    ),
    "department": fields.Field(
        column_name="department",
        attribute="department",
        widget=ForeignKeyWidget(Department, field="name"),
    ),
    "team": fields.Field(
        column_name="team",
        attribute="team",
        widget=ForeignKeyWidget(Team, field="name"),
    ),
    "chapter": fields.Field(
        column_name="chapter",
        attribute="chapter",
        widget=ForeignKeyWidget(Chapter, field="name"),
    ),
    "tribe": fields.Field(
        column_name="tribe",
        attribute="tribe",
        widget=ForeignKeyWidget(Tribe, field="name"),
    ),
    "mentioned_users": fields.Field(
        column_name="mentioned_users",
        attribute="mentioned_users",
        widget=ManyToManyWidget(User, field="name"),
    ),
    "linked_notes": fields.Field(
        column_name="linked_notes",
        attribute="linked_notes",
        widget=ManyToManyWidget(Note, field="title"),
    ),
}


class BaseModelResource(resources.ModelResource):
    lookup_field = "name"

    def get_instance(self, instance_loader, row):
        name = row.get(self.lookup_field)
        if name:
            try:
                return self._meta.model.objects.get(name=name)
            except self._meta.model.DoesNotExist:
                return None
        return None


@admin.register(Department)
class DepartmentAdmin(BaseModelAdmin):
    list_display = ("name", "date_created", "date_updated")
    fields = ("uuid", "name", "description", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام دپارتمان"


@admin.register(Tribe)
class TribeAdmin(BaseModelAdmin):
    class TribeResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]

        class Meta:
            model = Tribe
            fields = ("name", "leader", "department")

    resource_class = TribeResource
    list_display = ("name", "department", "leader", "date_created", "date_updated",)
    fields = ("uuid","name", ("department", "leader"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام قبیله، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Chapter)
class ChapterAdmin(BaseModelAdmin):
    list_display = ("name", "department", "leader", "date_created", "date_updated",)
    fields = ("uuid", "name", ("department", "leader"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام چپتر، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    class TeamResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]
        tribe = RESOURCE_FIELDS["tribe"]

        class Meta:
            model = Team
            fields = ("name", "leader", "department", "tribe")

    resource_class = TeamResource
    list_display = ("name", "department", "leader", "tribe", "date_created", "date_updated",)
    fields = ("uuid", "name", ("department", "leader", "tribe"), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام تیم، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Committee)
class CommitteeAdmin(BaseModelAdmin):
    list_display = ("name", "date_created", "date_updated",)
    fields = ("uuid", "name", "description", "members", ("date_created", "date_updated"),)
    filter_horizontal = ("members",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام کمیته"


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    class UserResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]
        team = RESOURCE_FIELDS["team"]
        chapter = RESOURCE_FIELDS["chapter"]
        lookup_field = "email"

        class Meta:
            model = User
            fields = ("email", "name", "gmail", "phone", "leader", "department", "team", "chapter",)

    resource_class = UserResource
    list_display = ("email", "name", "phone", "department", "chapter", "team", "leader", "date_created", "date_updated",)
    fields = ("uuid", "name", "phone", ("email", "gmail"), ("department", "chapter", "team", "leader", "committee"), ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "email")
    search_fields = ["email", "name", "phone"]
    search_help_text = "جستجو در نام کاربر، ایمیل، موبایل"


@admin.register(Note)
class NoteAdmin(BaseModelAdmin):
    class NoteResource(BaseModelResource):
        owner = RESOURCE_FIELDS["owner"]
        mentioned_users = RESOURCE_FIELDS["mentioned_users"]
        linked_notes = RESOURCE_FIELDS["linked_notes"]
        lookup_field = "uuid"

        class Meta:
            model = Note
            fields = ("uuid", "owner", "title", "content", "date", "type", "mentioned_users", "summary", "linked_notes",)

    resource_class = NoteResource
    list_display = ("title", "type", "owner", "date", "date_created", "date_updated")
    fields = ( "uuid", ("title", "type"), ("owner", "date"), "content", "mentioned_users", "summary", "is_public", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated", "mentioned_users")
    ordering = ("-date_updated", "title")
    search_fields = ["title", "owner__name", "owner__email"]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده"


@admin.register(Feedback)
class FeedbackAdmin(BaseModelAdmin):
    list_display = ("uuid", "owner", "note", "date_created", "date_updated")
    fields = ("uuid", ("owner", "note"), "content", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["owner__name", "owner__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"


@admin.register(NoteUserAccess)
class NoteUserAccessAdmin(BaseModelAdmin):
    list_display = ("uuid", "note", "user", "can_view", "can_edit", "can_write_summary", "can_write_feedback", "can_view_feedbacks", "date_created", "date_updated",)
    fields = ("uuid", "note", "user", "can_view", "can_edit", "can_write_summary", "can_write_feedback", "can_view_feedbacks", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["user__name", "user__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

# fmt: on
