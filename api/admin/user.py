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
        product_manager = RESOURCE_FIELDS["product_manager"]
        hrbp = RESOURCE_FIELDS["hrbp"]
        lookup_field = "email"

        class Meta:
            model = User
            import_id_fields = ("email",)
            fields = ("email", "name", "gmail", "phone", "leader", "level", "department", "team", "chapter", "organization", "product_manager", "hrbp", )

    resource_class = UserResource
    list_display = ("email", "name", "phone", "department", "chapter", "team", "organization", "leader", "agile_coach", "product_manager", "hrbp", "date_created", "date_updated",)
    fields = ("uuid", "name", "phone", ("email", "gmail"), ("department", "chapter", "team", "organization", "level", "leader", "agile_coach", "committee", "product_manager", "hrbp", ), ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "email")
    search_fields = ["email", "name", "phone"]
    search_help_text = "جستجو در نام کاربر، ایمیل، موبایل"
