from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from .base import MerlinBaseModel
from api.models.organization import ValueTag, ValueSection
from api.models.cycle import Cycle

__all__ = ['NoteType', 'NoteSubmitStatus', 'SummarySubmitStatus', 'Note', 'Feedback', 'Summary', 'NoteUserAccess', 'Vibe',
           'OneOnOne', 'OneOnOneTagLink', 'leader_permissions']

class NoteType(models.TextChoices):
    GOAL = "Goal", "هدف"
    MEETING = "Meeting", "جلسه"
    Personal = "Personal", "شخصی"
    TASK = "Task", "فعالیت"
    Proposal = "Proposal", "پروپوزال"
    Message = "Message", "پیام"
    Template = "Template", "قالب"
    ONE_ON_ONE = "OneOnOne", "یک‌به‌یک"

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


class Note(MerlinBaseModel):
    owner = models.ForeignKey("api.User", on_delete=models.CASCADE, verbose_name="نویسنده")
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
        "api.User",
        blank=True,
        related_name="mentioned_users",
        verbose_name="کاربران منشن شده",
    )
    is_public = models.BooleanField(default=False, verbose_name="عمومی")
    read_by = models.ManyToManyField("api.User", related_name="read_notes", blank=True)
    linked_notes = models.ManyToManyField(
        "Note", related_name="connected_notes", blank=True, verbose_name="پیوندها"
    )
    submit_status = models.IntegerField(
        choices=NoteSubmitStatus.choices,
        default=NoteSubmitStatus.default(),
        verbose_name="وضعیت",
    )
    cycle = models.ForeignKey("api.cycle", on_delete=models.PROTECT, verbose_name="دوره",
                              blank=True, null=True, )

    def is_sent_to_committee(self):
        return self.type == NoteType.Proposal and self.submit_status in (NoteSubmitStatus.PENDING,
                                                                         NoteSubmitStatus.REVIEWED)

    def has_summary_with_done_submit_status(self):
        """
        Checks if this note has an associated summary and if summary status is 'done'.
        """
        return hasattr(self, 'summary') and self.summary.submit_status == SummarySubmitStatus.DONE


    class Meta:
        verbose_name = "یادداشت"
        verbose_name_plural = "یادداشت‌ها"

    def __str__(self):
        return self.title


class Feedback(MerlinBaseModel):
    owner = models.ForeignKey("api.User", on_delete=models.CASCADE, verbose_name="نویسنده")
    content = models.TextField(verbose_name="محتوا")
    note = models.ForeignKey(Note, on_delete=models.CASCADE, verbose_name="یادداشت")
    cycle = models.ForeignKey("api.cycle", on_delete=models.PROTECT, verbose_name="دوره",
                              blank=True, null=True)

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
    cycle = models.ForeignKey("api.cycle", on_delete=models.PROTECT, verbose_name="دوره",
                              blank=True, null=True)

    class Meta:
        verbose_name = "جمع‌بندی"
        verbose_name_plural = "جمع‌بندی‌ها"

    def __str__(self):
        return "جمع‌بندیِ " + str(self.note)


                                                        # FUTURE ENHANCEMENT: Move this to api/services
class NoteUserAccess(MerlinBaseModel):
    user = models.ForeignKey(
        "api.User", on_delete=models.CASCADE, null=True, verbose_name="کاربر"
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
                "can_view_summary": note.has_summary_with_done_submit_status(),
                "can_write_summary": note.type == NoteType.GOAL,
                "can_view_feedbacks": True,
                "can_write_feedback": True,
            },
        )

        if note.type == NoteType.Personal:
            return

        # if note.type == NoteType.ONE_ON_ONE:
        #     return
        
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
        committee = note.owner.committee
        if committee is not None:
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

        # Mentioned users
        for user in note.mentioned_users.all():
            if committee is not None and user in committee.members.all():
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


class Vibe(models.TextChoices):
    HAPPY = ":)", "😊"
    NEUTRAL = ":|", "😐"
    SAD = ":(", "☹️"

class OneOnOne(MerlinBaseModel):
    """Detail table linked 1-to-1 with a generic Note row."""

    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name="one_on_one")
    organisation = models.ForeignKey(
        "api.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    member = models.ForeignKey(
        "api.User", on_delete=models.CASCADE, related_name="one_on_ones"
    )
    # --- 400-char summaries ---
    personal_summary = models.CharField(max_length=400, null=True, blank=True)
    career_summary = models.CharField(max_length=400, null=True, blank=True)
    communication_summary = models.CharField(max_length=400, null=True, blank=True)    
    performance_summary = models.CharField(max_length=400)

    # Actions text
    actions = models.TextField()

    # Vibes
    leader_vibe = models.CharField(max_length=2, choices=Vibe.choices)
    member_vibe = models.CharField(max_length=2, choices=Vibe.choices, null=True)

    # Cycle auto-filled in serializer
    cycle = models.ForeignKey(Cycle, on_delete=models.PROTECT)

    tags = models.ManyToManyField(
        ValueTag, through="OneOnOneTagLink", related_name="one_on_one_tags"
    )

    extra_notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "One-on-One"
        verbose_name_plural = "One-on-Ones"
        ordering = ("-date_created",)

    def __str__(self):
        return f"1-on-1 • {self.member} • {self.note.date}"

class OneOnOneTagLink(models.Model):
    one_on_one = models.ForeignKey(OneOnOne, on_delete=models.CASCADE)
    tag = models.ForeignKey(ValueTag, on_delete=models.CASCADE)
    section = models.CharField(max_length=32, choices=ValueSection.choices)

    class Meta:
        unique_together = ("one_on_one", "tag", "section")
        verbose_name = "One-on-One Tag Link"
        verbose_name_plural = "One-on-One Tag Links"