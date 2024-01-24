import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class MerlinBaseModel(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(
        _("Date Created"), null=True, blank=True, auto_now_add=True
    )

    date_updated = models.DateTimeField(
        _("Date Updated"), null=True, blank=True, auto_now=True
    )

    class Meta:
        abstract = True


class NoteType(models.TextChoices):
    GOAL = "Goal"
    MEETING = "Meeting"
    Personal = "Personal"

    @classmethod
    def default(cls):
        return cls.GOAL


class Note(MerlinBaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    content = models.TextField()
    date = models.DateField()
    type = models.CharField(
        max_length=128, choices=NoteType.choices, default=NoteType.default()
    )
