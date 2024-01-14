from django.contrib.auth.models import User
from django.db import models


class NoteType(models.TextChoices):
    GOAL = "Goal"
    MEETING = "Meeting"
    Personal = "Personal"

    @classmethod
    def default(cls):
        return cls.GOAL


class Note(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=512)
    content = models.TextField()
    date = models.DateField()
    type = models.CharField(
        max_length=128, choices=NoteType.choices, default=NoteType.default()
    )
