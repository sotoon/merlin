from django.db import models
from api.models.base import MerlinBaseModel

class TimelineEventType(models.TextChoices):
    ONE_ON_ONE_CREATED = "1on1_created", "ایجاد ۱×۱"
    ONE_ON_ONE_UPDATED = "1on1_updated", "ویرایش ۱×۱"

class UserTimeline(MerlinBaseModel):
    """Lightweight denormalised log for profile timeline & analytics."""

    user       = models.ForeignKey("api.User",  on_delete=models.CASCADE)
    event_type = models.CharField(max_length=32, choices=TimelineEventType.choices)
    object_id  = models.PositiveBigIntegerField()
    cycle      = models.ForeignKey("api.Cycle", on_delete=models.PROTECT)
    extra_json = models.JSONField(default=dict, blank=True)

    class Meta:
        index_together = (("user", "date_created"),)
        ordering       = ("-date_created",)

    def __str__(self):
        return f"{self.user} – {self.event_type} @ {self.created_at:%Y-%m-%d}"