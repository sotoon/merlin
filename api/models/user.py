from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.models.base import MerlinBaseModel
from api.models.note import Note, NoteUserAccess, leader_permissions
from api.models.role import RoleScope

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
    organization = models.ForeignKey(
        "Organization", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ارگانیزیشن"
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
    product_manager = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="product_manager_users",
        verbose_name="PM/پروداکت منجر",
    )
    hrbp = models.ForeignKey(
        "api.User",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="hrbp_users",
        verbose_name="اچ‌آربی‌پی",
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
            role_scope = role.role_scope.lower()
            role_type = role.role_type.lower()
            member = None

            if role.role_scope == RoleScope.USER:
                member = getattr(self, role_type)
            else:
                scope_object = getattr(self, role_scope)
                if scope_object:
                    member = getattr(scope_object, role_type)

            if member:
                committee_role_members.add(member)
        return committee_role_members

    def ensure_new_leader_note_accesses(self, new_leader):
        notes = Note.objects.filter(type__in=leader_permissions.keys(), owner=self)
        for note in notes:
            NoteUserAccess.ensure_note_predefined_accesses(note)


    def save(self, *args, **kwargs):
        self.username = self.email
        if self.pk is not None: # Check if the object is being updated (not created)
            original = User.objects.get(pk=self.pk)
            if self.leader != original.leader:
                self.ensure_new_leader_note_accesses(self.leader)
        super().save(*args, **kwargs)

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
