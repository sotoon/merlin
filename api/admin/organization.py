from django.contrib import admin

from .base import BaseModelAdmin, BaseModelResource, RESOURCE_FIELDS
from api.models.organization import Organization, Department, Tribe, Chapter, Team, Committee, ValueTag, OrgValueTag, PayBand


__all__ = ['OrganizationAdmin', 'DepartmentAdmin', 'TribeAdmin', 'ChapterAdmin', 'TeamAdmin', 'CommitteeAdmin', 'ValueTagAdmin', 'OrgValueTagAdmin', 'PayBandAdmin']


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
    search_fields = ["name"]


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
            fields = ("name", "leader", "department", "product_director", "engineering_director",)

    resource_class = TribeResource
    list_display = ("name", "department", "leader", "product_director", "engineering_director", "date_created", "date_updated",)
    fields = ("uuid","name", ("department", "leader", "product_director", "engineering_director", ), "description", ("date_created", "date_updated"),)
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
    fields = ("uuid", "name", "description", "members", "roles", ("date_created", "date_updated",),)
    filter_horizontal = ("members", "roles",)
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("-date_created", "name")
    search_fields = ["name"]
    search_help_text = "جستجو در نام کمیته"


@admin.register(ValueTag)
class ValueTagAdmin(BaseModelAdmin):
    list_display = ("name_en", "name_fa", "section", "date_created", "date_updated")
    fields = ("uuid", "name_en", "name_fa", "section", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("section", "name_en")
    search_fields = ["name_en", "name_fa"]
    list_filter = ["section"]
    search_help_text = "Search by English or Persian name"


@admin.register(OrgValueTag)
class OrgValueTagAdmin(admin.ModelAdmin):
    list_display = ("organisation", "tag", "is_enabled")
    list_display_links = ("tag",)
    list_editable = ("is_enabled",)
    fields = ("organisation", "tag", "is_enabled")
    list_filter = ["organisation", "is_enabled", "tag__section"]
    search_fields = ["tag__name_en", "tag__name_fa", "organisation__name"]
    autocomplete_fields = ["organisation", "tag"]
    search_help_text = "Search by tag name or organisation name"
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('organisation', 'tag')


@admin.register(PayBand)
class PayBandAdmin(BaseModelAdmin):
    list_display = ("number", "date_created", "date_updated")
    fields = ("uuid", "number", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    ordering = ("number",)
    search_fields = ["number"]
