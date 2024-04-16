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
    Summary,
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
    "committee": fields.Field(
        column_name="committee",
        attribute="committee",
        widget=ForeignKeyWidget(Committee, field="name"),
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
    "note": fields.Field(
        column_name="note",
        attribute="note",
        widget=ForeignKeyWidget(Note, field="uuid"),
    )
}


class BaseModelResource(resources.ModelResource):
    lookup_field = "name"

    def get_instance(self, instance_loader, row):
        field_value = row.get(self.lookup_field)
        if field_value:
            try:
                return self._meta.model.objects.get(**{self.lookup_field: field_value})
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
        committee = RESOURCE_FIELDS["committee"]
        lookup_field = "email"

        class Meta:
            model = User
            import_id_fields = ("email",)
            fields = ("email", "name", "gmail", "phone", "leader", "level", "department", "team", "chapter",)

    resource_class = UserResource
    list_display = ("email", "name", "phone", "department", "chapter", "team", "leader", "agile_coach", "date_created", "date_updated",)
    fields = ("uuid", "name", "phone", ("email", "gmail"), ("department", "chapter", "team", "level", "leader", "agile_coach", "committee"), ("date_created", "date_updated"),)
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
            fields = ("uuid", "owner", "title", "content", "date", "type", "mentioned_users", "linked_notes",)

    resource_class = NoteResource
    list_display = ("title", "type", "owner", "date", "date_created", "date_updated")
    fields = ( "uuid", ("title", "type"), ("owner", "date", "period", "year"), "content", "mentioned_users", "is_public", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated", "mentioned_users")
    ordering = ("-date_updated", "title")
    search_fields = ["uuid", "title", "owner__name", "owner__email"]
    search_help_text = "جستجو در عنوان، نام نویسنده، ایمیل نویسنده"


@admin.register(Feedback)
class FeedbackAdmin(BaseModelAdmin):
    list_display = ("uuid", "owner", "note", "date_created", "date_updated")
    fields = ("uuid", ("owner", "note"), "content", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["owner__name", "owner__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

@admin.register(Summary)
class SummaryAdmin(BaseModelAdmin):
    class SummaryResource(BaseModelResource):
        note = RESOURCE_FIELDS["note"]

        class Meta:
            model = Summary
            fields = ("uuid", "note", "content", "performance_label", "ladder_change", "bonus", "salary_change", "committee_date",)
    resource_class = SummaryResource
    list_display = ("uuid", "note", "performance_label", "committee_date", "date_created", "date_updated")
    fields = ("uuid", "note", "content", "performance_label", "ladder_change", "bonus", "salary_change", "committee_date", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["note__title", "note__owner__name", "note__owner__email"]
    search_help_text = "جستجو در عنوان یادداشت، نام نویسنده، ایمیل نویسنده"


@admin.register(NoteUserAccess)
class NoteUserAccessAdmin(BaseModelAdmin):
    list_display = ("uuid", "note", "user", "can_view", "can_edit", "can_write_summary", "can_write_feedback", "can_view_feedbacks", "date_created", "date_updated",)
    fields = ("uuid", "note", "user", "can_view", "can_edit", "can_write_summary", "can_write_feedback", "can_view_feedbacks", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "uuid")
    search_fields = ["user__name", "user__email", "note__title"]
    search_help_text = "جستجو در نام کاربر، ایمیل کاربر، عنوان یادداشت"

# fmt: on
