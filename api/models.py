import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


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


class NoteType(models.TextChoices):
    GOAL = "Goal", "هدف"
    MEETING = "Meeting", "جلسه"
    Personal = "Personal", "شخصی"
    TASK = "Task", "فعالیت"
    Proposal = "Proposal", "پروپوزال"
    Message = "Message", "پیام"
    Template = "Template", "قالب"

    @classmethod
    def default(cls):
        return cls.GOAL


class NoteSubmitStatus(models.IntegerChoices):
    INITIAL_SUBMIT = 1, _("ثبت اولیه")
    PENDING = 2, _("در حال بررسی")
    REVIEWED = 3, _("ثبت نهایی")

    @classmethod
    def default(cls):
        return cls.INITIAL_SUBMIT

class SummarySubmitStatus(models.IntegerChoices):
    INITIAL_SUBMIT = 1, _("ثبت اولیه")
    DONE = 2, _("نهایی‌ شده")

    @classmethod
    def default(cls):
        return cls.INITIAL_SUBMIT


leader_permissions = {
    NoteType.GOAL: {
        "can_view": True,
        "can_edit": False,
        "can_view_summary": True,
        "can_write_summary": True,
        "can_view_feedbacks": False,
        "can_write_feedback": True,
    }, NoteType.Proposal: {
        "can_view": True,
        "can_edit": False,
        "can_view_summary": True,
        "can_write_summary": True,
        "can_write_feedback": True,
        "can_view_feedbacks": True,
    }
}


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


class Note(MerlinBaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="نویسنده")
    title = models.CharField(max_length=512, verbose_name="عنوان")
    content = models.TextField(verbose_name="محتوا")
    date = models.DateField(verbose_name="تاریخ")
    period = models.IntegerField(default=0, verbose_name="دوره")
    year = models.IntegerField(default=1400, verbose_name="سال")
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
    is_public = models.BooleanField(default=False, verbose_name="عمومی")
    read_by = models.ManyToManyField(User, related_name="read_notes", blank=True)
    linked_notes = models.ManyToManyField(
        "Note", related_name="connected_notes", blank=True, verbose_name="پیوندها"
    )
    submit_status = models.IntegerField(
        choices=NoteSubmitStatus.choices,
        default=NoteSubmitStatus.default(),
        verbose_name="وضعیت",
    )

    def is_sent_to_committee(self):
        return self.type == NoteType.Proposal and self.submit_status in (NoteSubmitStatus.PENDING,
                                                                         NoteSubmitStatus.REVIEWED)

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


class Summary(MerlinBaseModel):
    content = models.TextField(verbose_name="محتوا")
    note = models.OneToOneField(Note, on_delete=models.CASCADE, verbose_name="یادداشت")
    performance_label = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="لیبل عملکردی"
    )
    ladder_change = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        verbose_name="تغییر در سطح لدر",
    )
    bonus = models.IntegerField(default=0, verbose_name="پاداش عملکردی")
    salary_change = models.FloatField(default=0, verbose_name="تغییر پله‌ی حقوقی")
    committee_date = models.DateField(
        blank=True, null=True, verbose_name="تاریخ برگزاری جلسه‌ی کمیته"
    )
    submit_status = models.IntegerField(
        choices=SummarySubmitStatus.choices,
        default=SummarySubmitStatus.default(),
        verbose_name="وضعیت",
    )

    class Meta:
        verbose_name = "جمع‌بندی"
        verbose_name_plural = "جمع‌بندی‌ها"

    def __str__(self):
        return "جمع‌بندیِ " + str(self.note)


class NoteUserAccess(MerlinBaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, verbose_name="کاربر"
    )
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, null=True, verbose_name="یادداشت"
    )
    can_view = models.BooleanField(default=False, verbose_name="مشاهده")
    can_edit = models.BooleanField(default=False, verbose_name="ویرایش")
    can_view_summary = models.BooleanField(default=False, verbose_name="مشاهده جمع‌بندی")
    can_write_summary = models.BooleanField(default=False, verbose_name="نوشتن جمع‌بندی")
    can_write_feedback = models.BooleanField(default=False, verbose_name="نوشتن فیدبک")
    can_view_feedbacks = models.BooleanField(
        default=False, verbose_name="مشاهده فیدبک‌ها"
    )

    class Meta:
        unique_together = (
            "user",
            "note",
        )
        verbose_name = "دسترسی"
        verbose_name_plural = "دسترسی‌ها"

    def __str__(self):
        return f"{self.user} - {self.note}"

    @classmethod
    def make_note_inaccessible_if_not(cls, user, note):
        cls.objects.filter(user=user, note=note).update(
            **{
                "can_view": False,
                "can_edit": False,
                "can_view_summary": False,
                "can_write_summary": False,
                "can_view_feedbacks": False,
                "can_write_feedback": False,
            },
        )

    @classmethod
    def ensure_note_predefined_accesses(cls, note):
        # Owner
        cls.objects.update_or_create(
            user=note.owner,
            note=note,
            defaults={
                "can_view": True,
                "can_edit": not note.is_sent_to_committee(),
                "can_view_summary": True,
                "can_write_summary": note.type == NoteType.GOAL,
                "can_view_feedbacks": True,
                "can_write_feedback": True,
            },
        )

        if note.type == NoteType.Personal:
            return

        # Leaders
        if (
            leader := note.owner.leader
        ) is not None:
            if note.type in leader_permissions.keys():
                cls.objects.update_or_create(
                    user=leader,
                    note=note,
                    defaults=leader_permissions[note.type],
                )
            else:
                cls.make_note_inaccessible_if_not(leader, note)

        # Agile Coach
        cls.objects.update_or_create(
            user=note.owner.agile_coach,
            note=note,
            defaults={
                "can_view": True,
                "can_edit": False,
                "can_view_summary": True,
                "can_write_summary": True,
                "can_write_feedback": True,
                "can_view_feedbacks": True,
            },
        )

        # Committee members
        if (
            committee := note.owner.committee
        ) is not None:
            for member in committee.members.all():
                if note.type == NoteType.Proposal:
                    cls.objects.update_or_create(
                        user=member,
                        note=note,
                        defaults={
                            "can_view": note.is_sent_to_committee(),
                            "can_edit": False,
                            "can_view_summary": True,
                            "can_write_summary": True,
                            "can_write_feedback": True,
                            "can_view_feedbacks": True,
                        },
                    )
                else:
                    cls.make_note_inaccessible_if_not(member, note)

        # Mentioned users
        for user in note.mentioned_users.all():
            if user in committee.members.all():
                continue
            cls.objects.update_or_create(
                user=user,
                note=note,
                defaults={
                    "can_view": True,
                    "can_edit": False,
                    "can_view_summary": False,
                    "can_write_summary": False,
                    "can_view_feedbacks": False,
                    "can_write_feedback": True
                },
            )
