from django.contrib import admin
from api.admin.base import BaseModelAdmin
from api.models import(
    Role,
)

__all__ = ['RoleAdmin']

@admin.register(Role)
class RoleAdmin(BaseModelAdmin):
    list_display = ("role_type", "role_scope", "date_created", "date_updated",)
    fields = ("role_type", "role_scope", ("date_created", "date_updated"),)
    readonly_fields = ("date_created", "date_updated",)
    ordering = ("-date_created", "role_scope")
    search_fields = ["role_type", "role_scope"]
    search_help_text = "جستجو در نوع نقش، سطح نقش"