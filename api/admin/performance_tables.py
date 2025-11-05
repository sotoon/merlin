from django.contrib import admin

from .base import BaseModelAdmin
from api.models import DataAccessOverride, CompensationSnapshot, SenioritySnapshot, OrgAssignmentSnapshot

__all__ = [
    "DataAccessOverrideAdmin",
    "CompensationSnapshotAdmin",
    "SenioritySnapshotAdmin",
    "OrgAssignmentSnapshotAdmin",
]


@admin.register(DataAccessOverride)
class DataAccessOverrideAdmin(BaseModelAdmin):
    list_display = ("user", "scope", "is_active", "expires_at", "date_created", "date_updated")
    list_filter = ("scope", "is_active")
    search_fields = ("user__name", "user__email", "reason")
    fields = ("uuid", "user", "granted_by", "scope", "reason", "is_active", "expires_at", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    autocomplete_fields = ("user", "granted_by")


@admin.register(CompensationSnapshot)
class CompensationSnapshotAdmin(BaseModelAdmin):
    list_display = ("user", "pay_band", "salary_change", "bonus_percentage", "effective_date", "date_created")
    list_filter = ("pay_band", "effective_date")
    search_fields = ("user__name", "user__email")
    fields = ("uuid", "user", "pay_band", "salary_change", "bonus_percentage", "effective_date", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    autocomplete_fields = ("user", "pay_band")


@admin.register(SenioritySnapshot)
class SenioritySnapshotAdmin(BaseModelAdmin):
    list_display = ("user", "ladder", "overall_score", "seniority_level", "effective_date", "date_created")
    list_filter = ("ladder", "seniority_level", "effective_date")
    search_fields = ("user__name", "user__email")
    fields = ("uuid", "user", "ladder", "title", "overall_score", "seniority_level", "details_json", "stages_json", "effective_date", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    autocomplete_fields = ("user", "ladder")


@admin.register(OrgAssignmentSnapshot)
class OrgAssignmentSnapshotAdmin(BaseModelAdmin):
    list_display = ("user", "leader", "team", "tribe", "chapter", "department", "effective_date")
    list_filter = ("team", "tribe", "chapter", "department")
    search_fields = ("user__name", "user__email", "leader__name", "team__name", "tribe__name")
    fields = ("uuid", "user", "leader", "team", "tribe", "chapter", "department", "effective_date", ("date_created", "date_updated"))
    readonly_fields = ("uuid", "date_created", "date_updated")
    autocomplete_fields = ("user", "leader", "team", "tribe", "chapter", "department") 