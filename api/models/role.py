from django.db import models
from api.models.base import MerlinBaseModel

__all__ = ['RoleType', 'RoleScope', 'Role', ]


class RoleType(models.TextChoices):
    LEADER = "Leader", "لیدر"  # chapter and user
    CTO = "CTO", "سی تی او"  # organization
    PRODUCT_DIRECTOR = "Product Director", "دیرکتور پروداکت"  # tribe
    VP = "VP", "وی پی"  # organization
    CEO = "CEO", "سی ای او"  # organization
    FUNCTION_OWNER = "Function Owner", "فانکشن اونر"  # organization
    PRODUCT_MANAGER = "Product Manager", "پروداکت منجر"  # user
    CPO = "CPO", "سی پی او"  # organization
    HR_MANAGER = "HR Manager", "اچ آر منجر"  # organization
    SALES_MANAGER = "Sales Manager", "مدیر فروش"  # organization
    CFO = "CFO", "سی اف او"  # organization
    HRBP = "HRBP", "اچ آر بی پی"
    ENGINEERING_DIRECTOR = "Engineering Director", "دیرکتور مهندسی"  # tribe

    @classmethod
    def default(cls):
        return cls.LEADER


class RoleScope(models.TextChoices):
    USER = "User", "کاربر"
    TEAM = "Team", "تیم"
    ORGANIZATION = "Organization", "سازمان"
    TRIBE = "TRIBE", "قبیله"
    CHAPTER = "Chapter", "چپتر"

    @classmethod
    def default(cls):
        return cls.USER


class Role(MerlinBaseModel):
    role_type = models.CharField(
        max_length=50,
        choices=RoleType.choices,
        default=RoleType.default,
    )
    role_scope = models.CharField(
        max_length=50,
        choices=RoleScope.choices,
        default=RoleScope.default,
    )

    class Meta:
        unique_together = ('role_type', 'role_scope')
        verbose_name = "نقش"
        verbose_name_plural = "نقش‌ها"

    def __str__(self):
        return f"{self.get_role_type_display()} - {self.get_role_scope_display()}"
