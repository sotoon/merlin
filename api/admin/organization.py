
from django.contrib import admin

from .base import BaseModelAdmin, BaseModelResource, RESOURCE_FIELDS
from api.models import Department, Tribe, Chapter, Team, Committee, Organization


__all__ = ['DepartmentAdmin', 'TribeAdmin', 'ChapterAdmin', 'TeamAdmin', 'CommitteeAdmin']


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
        product_director = RESOURCE_FIELDS["product_director"]
        engineering_director = RESOURCE_FIELDS["engineering_director"]

        class Meta:
            model = Tribe
            fields = ("name", "leader", "department", "product_director", "engineering_director", )

    resource_class = TribeResource
    list_display = ("name", "department", "leader", "product_director", "engineering_director", "date_created", "date_updated",)
    fields = ("uuid","name", ("department", "leader", "product_director", "engineering_director", ), "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name", "department__name", "leader__name", "leader__email"]
    search_help_text = "جستجو در نام قبیله، نام دپارتمان، نام لیدر، ایمیل لیدر "


@admin.register(Organization)
class OrganizationAdmin(BaseModelAdmin):
    class OrganizationResource(BaseModelResource):
        class Meta:
            model = Organization
            fields = ("name", "cto", "vp", "ceo", "function_owner", "cpo", "hr_manager", "sales_manager", "cfo", "description", )

    resource_class = OrganizationResource
    list_display = ("name", "date_created", "date_updated",)
    fields = ("uuid","name", "cto", "vp", "ceo", "function_owner", "cpo", "hr_manager", "sales_manager", "cfo", "description", ("date_created", "date_updated"),)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    # search_fields = ["name", "cto__name", "cto__email"]
    # search_help_text = "جستجو در نام قبیله، نام دپارتمان، نام لیدر، ایمیل لیدر "
    search_fields = ["name"]


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
    fields = ("uuid", "name", "description", "members", "roles", ("date_created", "date_updated"),)
    filter_horizontal = ("members",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام کمیته"
