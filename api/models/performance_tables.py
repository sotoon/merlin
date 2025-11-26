from django.db import models

from api.models.base import MerlinBaseModel
from api.models.ladder import Ladder

__all__ = [
    "OrgAssignmentSnapshot",
    "CompensationSnapshot",
    "SenioritySnapshot",
    "DataAccessOverride",
]


class OrgAssignmentSnapshot(MerlinBaseModel):
    user = models.ForeignKey("api.User", on_delete=models.CASCADE, related_name="org_snapshots")
    leader = models.ForeignKey(
        "api.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="org_leader_snapshots",
    )
    team = models.ForeignKey("api.Team", on_delete=models.SET_NULL, null=True, blank=True)
    tribe = models.ForeignKey("api.Tribe", on_delete=models.SET_NULL, null=True, blank=True)
    chapter = models.ForeignKey("api.Chapter", on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey("api.Department", on_delete=models.SET_NULL, null=True, blank=True)
    effective_date = models.DateField()

    class Meta:
        verbose_name = "اسنپ‌شات انتساب سازمانی"
        verbose_name_plural = "اسنپ‌شات‌های انتساب سازمانی"
        ordering = ("-effective_date",)
        indexes = [
            models.Index(fields=["user", "effective_date"]),
            models.Index(fields=["leader", "effective_date"]),
            models.Index(fields=["team", "effective_date"]),
            models.Index(fields=["tribe", "effective_date"]),
        ]

    def __str__(self):
        return f"{self.user} • {self.team or '-'} • {self.leader or '-'} @ {self.effective_date}"


class CompensationSnapshot(MerlinBaseModel):
    user = models.ForeignKey("api.User", on_delete=models.PROTECT, related_name="comp_snapshots")
    pay_band = models.ForeignKey("api.PayBand", on_delete=models.PROTECT, null=True, blank=True)
    salary_change = models.FloatField(default=0.0, help_text="Delta steps applied; supports 0.5 increments")
    bonus_percentage = models.FloatField(default=0, help_text="Bonus as percentage of annual salary")
    effective_date = models.DateField()
    source_event = models.ForeignKey("api.TimelineEvent", null=True, blank=True, on_delete=models.SET_NULL)
    is_redacted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "اسنپ‌شات جبران خدمات"
        verbose_name_plural = "اسنپ‌شات‌های جبران خدمات"
        ordering = ("-effective_date",)
        indexes = [
            models.Index(fields=["user", "effective_date"]),
            models.Index(fields=["pay_band", "effective_date"]),
            # Unique partial index for source_event disambiguation
            models.Index(
                fields=["user", "effective_date", "source_event"],
                condition=models.Q(source_event__isnull=False),
                name="unique_comp_snapshot_per_event"
            ),
        ]

    def __str__(self):
        return f"{self.user} • PayBand {self.pay_band_id or '-'} • Bonus {self.bonus_percentage}%"


class SenioritySnapshot(MerlinBaseModel):
    class SeniorityLevel(models.TextChoices):
        JUNIOR = "JUNIOR", "Junior"
        MID = "MID", "Mid"
        SENIOR = "SENIOR", "Senior"
        PRINCIPAL = "PRINCIPAL", "Principal"

    user = models.ForeignKey("api.User", on_delete=models.CASCADE, related_name="seniority_snapshots")
    ladder = models.ForeignKey(Ladder, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(max_length=256)
    overall_score = models.FloatField(default=0)
    details_json = models.JSONField(default=dict, blank=True)
    stages_json = models.JSONField(default=dict, blank=True)
    seniority_level = models.CharField(
        max_length=20,
        choices=SeniorityLevel.choices,
        null=True,
        blank=True,
        verbose_name="Seniority Level",
        help_text="Seniority classification (Junior/Mid/Senior/Principal) for data analytics",
    )
    effective_date = models.DateField()
    source_event = models.ForeignKey("api.TimelineEvent", null=True, blank=True, on_delete=models.SET_NULL)
    is_redacted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "اسنپ‌شات سطح فنی"
        verbose_name_plural = "اسنپ‌شات‌های سطح فنی"
        ordering = ("-effective_date",)
        indexes = [
            models.Index(fields=["user", "effective_date"]),
            models.Index(fields=["ladder", "effective_date"]),
            # Unique partial index for source_event disambiguation
            models.Index(
                fields=["user", "ladder", "effective_date", "source_event"],
                condition=models.Q(source_event__isnull=False),
                name="unique_sen_snapshot_per_event"
            ),
        ]

    def __str__(self):
        return f"{self.user} • {self.ladder} • {self.overall_score}"


class DataAccessOverride(MerlinBaseModel):
    class Scope(models.TextChoices):
        ALL = "ALL", "All users"
        TECH = "TECH", "Technical users"
        PRODUCT = "PRODUCT", "Product users"

    user = models.ForeignKey("api.User", on_delete=models.CASCADE, related_name="data_access_overrides")
    granted_by = models.ForeignKey("api.User", on_delete=models.PROTECT, related_name="granted_access_overrides")
    scope = models.CharField(max_length=16, choices=Scope.choices)
    reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Data Access Override"
        verbose_name_plural = "Data Access Overrides"
        indexes = [
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"Override({self.scope}) for {self.user}" 