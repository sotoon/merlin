from django.db import models
from api.models.base import MerlinBaseModel
from django.core.exceptions import ValidationError
from django.apps import apps

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
    MAINTAINER = "Maintainer", "نگهدارنده"  # organization

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

    def _normalize_attr(self, value: str) -> str:
        """Helper: convert 'Product Director' → 'product_director' to match model fields."""
        return value.lower().replace(" ", "_")

    def clean(self):
        """Ensure (role_type, role_scope) maps to a real attribute on the target model.
        Allows future role types/scopes as long as the field exists.
        """
        # Avoid circular imports by resolving lazily via apps
        from api.models import RoleScope  # local import only for Enum access

        scope_map = {
            RoleScope.USER: "api.User",
            RoleScope.TEAM: "api.Team",
            RoleScope.TRIBE: "api.Tribe",
            RoleScope.ORGANIZATION: "api.Organization",
            RoleScope.CHAPTER: "api.Chapter",
        }
        target_model_label = scope_map.get(self.role_scope)
        if not target_model_label:
            return  # unknown scope - let DB handle/ other validation

        target_model = apps.get_model(target_model_label)
        attr_name = self._normalize_attr(self.role_type)
        if not hasattr(target_model, attr_name):
            raise ValidationError(
                {
                    "role_scope": (
                        f"'{self.get_role_type_display()}' cannot use scope "
                        f"{self.get_role_scope_display()} – attribute '{attr_name}' "
                        f"does not exist on {target_model.__name__}."
                    )
                }
            )

    def save(self, *args, **kwargs):
        # Run full_clean() to enforce validation rules even outside admin
        self.full_clean()
        super().save(*args, **kwargs)