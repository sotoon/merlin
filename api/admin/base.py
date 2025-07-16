from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from import_export import fields, resources

from api.models import (
    Chapter,
    Committee,
    Department,
    Note,
    Team,
    Tribe,
    User,
    Organization,
)


__all__ = ['BaseModelAdmin', 'BaseModelResource', 'RESOURCE_FIELDS']


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
    "product_manager": fields.Field(
        column_name="product_manager",
        attribute="product_manager",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "hrbp": fields.Field(
        column_name="hrbp",
        attribute="hrbp",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "director": fields.Field(
        column_name="director",
        attribute="director",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "product_director": fields.Field(
        column_name="product_director",
        attribute="product_director",
        widget=ForeignKeyWidget(User, field="email"),
    ),
    "engineering_director": fields.Field(
        column_name="engineering_director",
        attribute="engineering_director",
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
    "organization": fields.Field(
        column_name="organization",
        attribute="organization",
        widget=ForeignKeyWidget(Organization, field="name"),
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

