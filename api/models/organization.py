from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.base import MerlinBaseModel
from api.models.user import User

__all__ = ['Organization', 'Department', 'Chapter', 'Tribe', 'Team', 'Committee', 'ValueSection', 'ValueTag', 'OrgValueTag']


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
        verbose_name = "سازمان"
        verbose_name_plural = "سازمان‌ها"

    def __str__(self):
        return self.name


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
    
# Values models
class ValueSection(models.TextChoices):
    PERSONAL = "personal", "بعد فردی"
    CAREER = "career", "مسیر رشد و انتظارات"
    PERFORMANCE = "performance", "مدیریت عملکرد"
    COMMUNICATION = "communication", "تعامل و مشتری‌محوری"

class ValueTag(MerlinBaseModel):
    """Canonical, organisation-agnostic behaviour/value tag."""

    name_en = models.CharField(max_length=128, unique=True)
    name_fa = models.CharField(max_length=128)
    section = models.CharField(max_length=32, choices=ValueSection.choices)

    class Meta:
        verbose_name = "Behaviour Tag"  # TODO: Persian verbose
        verbose_name_plural = "Behaviour Tags"

    def __str__(self):
        return self.name_en

class OrgValueTag(models.Model):
    """Enable/disable a BehaviourTag per organisation."""

    organisation = models.ForeignKey(
        "api.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    tag = models.ForeignKey(ValueTag, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("organisation", "tag")
        verbose_name = "Organisation Behaviour Tag"  # TODO: Persian
        verbose_name_plural = "Organisation Behaviour Tags"

    def __str__(self):
        return f"{self.organisation or 'GLOBAL'} – {self.tag}"
