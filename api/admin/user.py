from django.contrib import admin

from .base import BaseModelAdmin, BaseModelResource, RESOURCE_FIELDS
from api.models import User


__all__ = ['UserAdmin']


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    class UserResource(BaseModelResource):
        leader = RESOURCE_FIELDS["leader"]
        department = RESOURCE_FIELDS["department"]
        team = RESOURCE_FIELDS["team"]
        chapter = RESOURCE_FIELDS["chapter"]
        organization = RESOURCE_FIELDS["organization"]
        committee = RESOURCE_FIELDS["committee"]
        lookup_field = "email"

        class Meta:
            model = User
            import_id_fields = ("email",)
            fields = ("email", "name", "gmail", "phone", "leader", "department", "team", "chapter", "organization",)

    resource_class = UserResource
    list_display = ("email", "name", "phone", "department", "chapter", "team", "leader", "agile_coach", "date_created", "date_updated", "organization")
    fields = ("uuid", "name", "phone", ("email", "gmail"), ("department", "chapter", "team", "leader", "agile_coach", "committee", "organization"), ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "email")
    search_fields = ["email", "name", "phone"]
    search_help_text = "جستجو در نام کاربر، ایمیل، موبایل"
