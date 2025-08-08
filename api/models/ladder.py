from django.db import models

from api.models.base import MerlinBaseModel

__all__ = [
    "Ladder",
    "LadderAspect",
    "LadderStage",
    "LadderLevel",
]


class Ladder(MerlinBaseModel):
    """Top-level ladder (e.g. Software, DevOps, Product)."""

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "لدر"
        verbose_name_plural = "لدرها"
        ordering = ("code",)

    def __str__(self):
        return self.name
    
    def get_max_level(self) -> int:
        """Get the maximum level for this ladder by checking LadderLevel objects."""
        return self.steps.aggregate(max_level=models.Max('level'))['max_level'] or 0


class LadderAspect(MerlinBaseModel):
    """A competency axis inside a ladder (e.g. Design, Implementation)."""

    ladder = models.ForeignKey(Ladder, on_delete=models.CASCADE, related_name="aspects")
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("ladder", "code")
        ordering = ("ladder", "order")
        verbose_name = "بعد لدر"
        verbose_name_plural = "ابعاد لدر"

    def __str__(self):
        return f"{self.ladder} • {self.name}"
    

class LadderStage(models.TextChoices):
    EARLY = "EARLY", "ابتدای سطح"
    MID = "MID", "میانه سطح"
    LATE = "LATE", "انتهای سطح"

    @classmethod
    def default(cls):
        return cls.EARLY


class LadderLevel(MerlinBaseModel):
    """Granular grade within an aspect (level + stage)."""

    ladder = models.ForeignKey(Ladder, on_delete=models.CASCADE, related_name="steps", default=None)
    aspect = models.ForeignKey(LadderAspect, on_delete=models.CASCADE, related_name="steps", default=None)
    level = models.PositiveIntegerField(default=1)
    stage = models.CharField(max_length=8, choices=LadderStage.choices, default=LadderStage.default())
    weight = models.FloatField(default=1.0, help_text="Optional weighting when averaging across aspects.")

    class Meta:
        unique_together = ("ladder", "aspect", "level", "stage")
        ordering = ("ladder", "aspect", "level", "stage")
        verbose_name = "سطح لدر"
        verbose_name_plural = "سطوح لدر"

    # Convenience --------------------------------------------------------------------------------
    STAGE_OFFSET = {LadderStage.EARLY: 0.0, LadderStage.MID: 0.3, LadderStage.LATE: 0.6}

    def numeric_value(self) -> float:
        """Return a float value, e.g. level 3 MID → 3.3."""
        return self.level + self.STAGE_OFFSET[self.stage]

    def __str__(self):
        return f"{self.ladder} • {self.aspect} L{self.level} {self.get_stage_display()}" 