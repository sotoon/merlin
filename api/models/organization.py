from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import MerlinBaseModel

__all__ = ['Department', 'Chapter', 'Tribe', 'Team', 'Committee', 'Organization', ]

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
        "api.User",
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
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tribe_leader",
        verbose_name="لیدر",
    )
    director = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tribe_director",
        verbose_name="دیرکتور",
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
        "api.User",
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
        "api.User", related_name="committee_members", verbose_name="اعضا"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    roles = models.ManyToManyField("api.Role", related_name='role_committees', blank=True)

    class Meta:
        verbose_name = "کمیته"
        verbose_name_plural = "کمیته‌ها"

    def __str__(self):
        return self.name


class Organization(MerlinBaseModel):
    name = models.CharField(max_length=256, verbose_name="نام")
    cto = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_cto",
        verbose_name="سی تی او",
    )
    vp = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_vp",
        verbose_name="وی پی",
    )
    ceo = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_ceo",
        verbose_name="سی ای او",
    )
    function_owner = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_function_owner",
        verbose_name="فانکشن اونر",
    )
    cpo = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_cpo",
        verbose_name="سی پی او",
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")

    class Meta:
        verbose_name = "ارگانیزیشن"
        verbose_name_plural = "ارگانیزیشن‌ها"

    def __str__(self):
        return self.name
