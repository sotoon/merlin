import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class MerlinBaseModel(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(
        "تاریخ ساخت", null=True, blank=True, auto_now_add=True
    )

    date_updated = models.DateTimeField(
        "تاریخ بروزرسانی", null=True, blank=True, auto_now=True
    )

    class Meta:
        abstract = True


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
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.name:
            return self.name
        return self.email

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class Department(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "دپارتمان"
        verbose_name_plural = "دپارتمان‌ها"

    def __str__(self):
        return self.name


class Chapter(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, verbose_name="دپارتمان"
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name="chapter_leader",
        verbose_name="لیدر",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "چپتر"
        verbose_name_plural = "چپترها"

    def __str__(self):
        return self.name


class Team(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, verbose_name="دپارتمان"
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name="team_leader",
        verbose_name="لیدر",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "تیم"
        verbose_name_plural = "تیم‌ها"

    def __str__(self):
        return self.name


class NoteType(models.TextChoices):
    GOAL = "Goal", "هدف"
    MEETING = "Meeting", "جلسه"
    Personal = "Personal", "شخصی"
    TASK = "Task", "فعالیت"

    @classmethod
    def default(cls):
        return cls.GOAL


class Note(MerlinBaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده")
    title = models.CharField(max_length=512, verbose_name="عنوان")
    content = models.TextField(verbose_name="محتوا")
    date = models.DateField(verbose_name="تاریخ")
    type = models.CharField(
        max_length=128,
        choices=NoteType.choices,
        default=NoteType.default(),
        verbose_name="نوع",
    )
    mentioned_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="mentioned_users",
        verbose_name="کاربران منشن شده",
    )

    class Meta:
        verbose_name = "یادداشت"
        verbose_name_plural = "یادداشت‌ها"

    def __str__(self):
        return self.title


class Feedback(MerlinBaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده")
    content = models.TextField(verbose_name="محتوا")
    note = models.ForeignKey(Note, on_delete=models.CASCADE, verbose_name="یادداشت")

    class Meta:
        unique_together = (
            "owner",
            "note",
        )
        verbose_name = "فیدبک"
        verbose_name_plural = "فیدبک‌ها"

    def __str__(self):
        return f"{self.owner} - {self.note}"
