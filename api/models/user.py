from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import logging

from api.models.base import MerlinBaseModel


__all__ = ['User']


logger = logging.getLogger(__name__)


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
    organization = models.ForeignKey(
        "Organization", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سازمان"
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        if self.name:
            return self.name
        return self.email

    @property
    def tribe(self):
        return self.team.tribe

    def get_committee_role_members(self):
        committee_role_members = set()

        for role in self.committee.roles.distinct():
            role_type_raw = role.role_type
            role_scope_raw = role.role_scope
            role_scope = role_scope_raw.lower()
            role_type = role_type_raw.lower().replace(" ", "_")  # normalize to attribute style
            member = None

            from api.models import RoleScope

            if role_scope_raw == RoleScope.USER:
                member = getattr(self, role_type, None)
            else:
                scope_object = getattr(self, role_scope, None)
                if scope_object:
                    member = getattr(scope_object, role_type, None)

            if member:
                committee_role_members.add(member)
            else:
                logger.warning("Unresolved committee role %s:%s for user %s (id=%s)", role.role_scope, role.role_type, self, self.pk)
        return committee_role_members

    def save(self, *args, **kwargs):
        self.username = self.email

        original_leader = None
        if self.pk is not None: # Check if the object is being updated (not created)
            original_leader = User.objects.get(pk=self.pk).leader
        
        super().save(*args, **kwargs)
        
        if original_leader != self.leader:
            # Local import to avoid circular import at module load time
            from api.services import ensure_leader_note_accesses
            ensure_leader_note_accesses(self, self.leader)

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"

    def get_leaders(self):
        leaders = []
        visited_ids = set()
        current = self.leader
        depth = 0
        max_depth = 10
        while current and depth < max_depth:
            if current.pk in visited_ids:
                break
            leaders.append(current)
            visited_ids.add(current.pk)
            current = current.leader
            depth += 1
        return leaders
