from django.db import models

from api.models.base import MerlinBaseModel

__all__ = ['Cycle']

class Cycle(MerlinBaseModel):
    name = models.CharField(max_length=150, verbose_name="نام دوره")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال‌سازی")

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
