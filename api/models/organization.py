from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

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
    hr_manager = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_hr_manager",
        verbose_name="مدیر اچ‌آر",
    )
    sales_manager = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_sales_manager",
        verbose_name="مدیر فروش",
    )
    cfo = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="organization_cfo",
        verbose_name="سی‌اف‌او",
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
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tribe_leader",
        verbose_name="لیدر",
    )
    product_director = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product_director_tribes",
        verbose_name="دیرکتور محصولی",
    )
    engineering_director = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="engineering_director_tribes",
        verbose_name="دیرکتور فنی",
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
        "api.User", related_name="committee_members", verbose_name="اعضا"
    )
    description = models.TextField(blank=True, verbose_name="توضیحات")
    roles = models.ManyToManyField("api.Role", related_name='role_committees', blank=True)

    class Meta:
        verbose_name = "کمیته"
        verbose_name_plural = "کمیته‌ها"

    def __str__(self):
        return self.name

    def clean(self):
        """Ensure every role attached to this committee resolves to an actual user for at least one committee member.
        If not, raise a ValidationError so admins notice mis-configuration early.
        """
        super().clean()

        # Skip when no roles or no sample user is available yet.
        if not self.roles.exists():
            return

        # Prefer a user that is explicitly assigned to this committee via FK
        sample_user = self.committee_users.first() if hasattr(self, "committee_users") else None
        # Fallback to members M2M if no FK user yet
        if sample_user is None:
            sample_user = self.members.first()

        if sample_user is None:
            return  # Nothing to validate without users

        from api.models import RoleScope  # Local import to avoid circular dependency

        unresolved = []
        for role in self.roles.all():
            role_scope = role.role_scope.lower()
            role_type = role.role_type.lower()
            member = None

            if role.role_scope == RoleScope.USER:
                member = getattr(sample_user, role_type, None)
            else:
                scope_object = getattr(sample_user, role_scope, None)
                if scope_object is not None:
                    member = getattr(scope_object, role_type, None)

            if member is None:
                unresolved.append(f"{role.get_role_scope_display()} / {role.get_role_type_display()}")

        if unresolved:
            raise ValidationError({
                "roles": _(f"These committee roles cannot be resolved for the current data: {', '.join(unresolved)}")
            })
    
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

# -------------------------------------------------------------
# Legacy stub for historical migrations only. Do NOT use.
# -------------------------------------------------------------


class CommitteeType(models.TextChoices):
    PROMOTION = "PROMOTION", "ارتقا"
    NOTICE = "NOTICE", "نوتیس"
    MAPPING = "MAPPING", "مپینگ اولیه"
    EVALUATION = "EVALUATION", "ارزیابی"

    @classmethod
    def default(cls):
        return cls.PROMOTION
