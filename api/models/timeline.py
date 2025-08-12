from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from api.models.base import MerlinBaseModel
from api.models.ladder import Ladder
from api.models.performance_tables import CompensationSnapshot, SenioritySnapshot
from api.models.organization import PayBand

__all__ = [
    "EventType",
    "TimelineEvent",
    "PayBand",
    "CompensationSnapshot",
    "SenioritySnapshot",
    "NoticeType",
    "Notice",
    "GrantType",
    "StockGrant",
    "TitleChange",
]

# ───────────────────────────────────────────────────────────────
# Enums
# ----------------------------------------------------------------

class EventType(models.TextChoices):
    SENIORITY_CHANGE = "SENIORITY_CHANGE", "تغییر سطح لدر"
    PAY_CHANGE = "PAY_CHANGE", "تغییر بسته‌ حقوقی"
    BONUS_PAYOUT = "BONUS_PAYOUT", "پرداخت پاداش"
    EVALUATION = "EVALUATION", "خروجی ارزیابی کمیته"
    MAPPING = "MAPPING", "بازنشانی روی لدر"
    TITLE_CHANGE = "TITLE_CHANGE", "تغییر عنوان شغلی"
    STOCK_GRANT = "STOCK_GRANT", "اعطای سهام"
    NOTICE = "NOTICE", "نوتیس"
    LADDER_CHANGED = "LADDER_CHANGED", "تغییر لدر"

    @classmethod
    def default(cls):
        return cls.EVALUATION


class NoticeType(models.TextChoices):
    PERFORMANCE = "PERFORMANCE", "عملکردی"
    CONDUCT = "CONDUCT", "رفتاری"
    OTHER = "OTHER", "سایر"

    @classmethod
    def default(cls):
        return cls.PERFORMANCE


class GrantType(models.TextChoices):
    RSU = "RSU", "RSU"
    OPTION = "OPTION", "Option"

    @classmethod
    def default(cls):
        return cls.RSU


# ───────────────────────────────────────────────────────────────
# Core tables
# ----------------------------------------------------------------


class TimelineEvent(MerlinBaseModel):
    """Unified feed of career-relevant events."""

    # Target employee
    user = models.ForeignKey("api.User", on_delete=models.PROTECT, related_name="timeline_events")
    event_type = models.CharField(max_length=32, choices=EventType.choices, default=EventType.default())
    summary_text = models.CharField(max_length=512)
    effective_date = models.DateField()

    # Generic relation to source artefact (Note, Summary, Notice, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # ACL bit-mask: SELF=1, COMMITTEE=2, LEADER=4, HR=8, EXEC=16
    visibility_mask = models.PositiveIntegerField(default=1)

    created_by = models.ForeignKey(
        "api.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_timeline_events"
    )

    class Meta:
        verbose_name = "رویداد پروفایل"
        verbose_name_plural = "رویدادهای پروفایل"
        ordering = ("-effective_date", "-date_created")

    def __str__(self):
        return f"{self.user} • {self.get_event_type_display()} • {self.effective_date}"


# ───────────────────────────────────────────────────────────────
# Lightweight artefact tables (HR manual entry)
# ----------------------------------------------------------------


class Notice(MerlinBaseModel):
    user = models.ForeignKey("api.User", on_delete=models.PROTECT)
    notice_type = models.CharField(max_length=16, choices=NoticeType.choices, default=NoticeType.default())
    description = models.TextField()
    committee_date = models.DateField()
    created_by = models.ForeignKey("api.User", on_delete=models.SET_NULL, null=True, related_name="notices_created")

    class Meta:
        verbose_name = "نوتیس"
        verbose_name_plural = "نوتیس‌ها"
        ordering = ("-committee_date",)

    def __str__(self):
        return f"{self.user} • {self.get_notice_type_display()} • {self.committee_date}"


class StockGrant(MerlinBaseModel):
    user = models.ForeignKey("api.User", on_delete=models.PROTECT)
    created_by = models.ForeignKey("api.User", on_delete=models.SET_NULL, null=True, related_name="stock_grants_created")
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "گرنت سهام"
        verbose_name_plural = "گرنت‌های سهام"
        ordering = ("-date_created",)

    def __str__(self):
        return f"{self.user} • {self.description[:30]}"


class TitleChange(MerlinBaseModel):
    user = models.ForeignKey("api.User", on_delete=models.PROTECT)
    old_title = models.CharField(max_length=256)
    new_title = models.CharField(max_length=256)
    reason = models.TextField(blank=True, null=True)
    effective_date = models.DateField()
    created_by = models.ForeignKey("api.User", on_delete=models.SET_NULL, null=True, related_name="title_changes_created")

    class Meta:
        verbose_name = "تغییر عنوان"
        verbose_name_plural = "تغییرات عنوان"
        ordering = ("-effective_date",)

    def __str__(self):
        return f"{self.user} • {self.old_title} → {self.new_title}"