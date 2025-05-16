from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import MerlinBaseModel
from api.services import ensure_leader_note_accesses

__all__ = ['User']

class User(MerlinBaseModel, AbstractUser):
    email = models.EmailField(unique=True, verbose_name="ایمیل سازمانی")
    name = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="نام"
    )
    gmail = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="جیمیل"
    )
    phone = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="موبایل"
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="دپارتمان",
    )
    chapter = models.ForeignKey(
        "Chapter", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="چپتر"
    )
    team = models.ForeignKey(
        "Team", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="تیم"
    )
    leader = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="لیدر"
    )
    agile_coach = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coachees",
        verbose_name="PR/اجایل کوچ",
    )
    committee = models.ForeignKey(
        "Committee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="committee_users",
        verbose_name="کمیته",
    )
    level = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="سطح"
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.name:
            return self.name
        return self.email

    def save(self, *args, **kwargs):
        self.username = self.email

        original_leader = None
        if self.pk is not None: # Check if the object is being updated (not created)
            original_leader = User.objects.get(pk=self.pk).leader
        
        super().save(*args, **kwargs)
        
        if original_leader != self.leader:
            ensure_leader_note_accesses(self, self.leader)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def get_leaders(self):
        leader = self.leader
        leaders = []
        count = 0
        max_count = 10
        while leader:
            leaders.append(leader)
            count += 1
            if max_count > count:
                break
        return leaders
