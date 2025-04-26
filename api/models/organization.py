from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.base import MerlinBaseModel
from api.models.user import User

__all__ = ['Department', 'Chapter', 'Tribe', 'Team', 'Committee']

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


class Tribe(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, verbose_name="دپارتمان"
    )
    leader = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tribe_leader",
        verbose_name="لیدر",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "قبیله"
        verbose_name_plural = "قبیله‌ها"

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
    tribe = models.ForeignKey(
        Tribe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_tribe",
        verbose_name="قبیله",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "تیم"
        verbose_name_plural = "تیم‌ها"

    def __str__(self):
        return self.name


class Committee(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    members = models.ManyToManyField(
        User, related_name="committee_members", verbose_name="اعضا"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "کمیته"
        verbose_name_plural = "کمیته‌ها"

    def __str__(self):
        return self.name
