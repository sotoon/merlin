from django.db import models

from api.models.base import MerlinBaseModel

__all__ = ['Cycle']

class Cycle(MerlinBaseModel):
    name = models.CharField(max_length=150, verbose_name="نام دوره")
    start_date = models.DateTimeField(verbose_name="تاریخ شروع")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال‌سازی")

    @classmethod
    def get_current_cycle(cls):
        cycle = cls.objects.filter(is_active=True).order_by('-start_date').first()
        if not cycle:
            raise ValueError("No active cycle found. Please create and activate a cycle first.")
        return cycle
        
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
