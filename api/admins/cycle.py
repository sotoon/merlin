from django.contrib import admin

from .base import BaseModelAdmin
from api.models import Cycle

@admin.register(Cycle)
class CycleAdmin(BaseModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
