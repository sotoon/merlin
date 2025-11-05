from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from .base import MerlinBaseModel
from api.models import (Cycle,
                        Committee,
                        ValueTag,
                        ValueSection,
                        )

__all__ = ['NoteType', 'ProposalType', 'NoteSubmitStatus', 'SummarySubmitStatus', 'Note', 'Comment', 'Feedback', 'FeedbackForm', 'FeedbackRequest', 'FeedbackRequestUserLink', 'FeedbackTagLink', 'Summary', 'NoteUserAccess', 'Vibe',
           'OneOnOne', 'OneOnOneTagLink', 'leader_permissions', 'committee_roles_permissions']

class NoteType(models.TextChoices):
    GOAL = "Goal", "هدف"
    MEETING = "Meeting", "جلسه"
    Personal = "Personal", "شخصی"
    TASK = "Task", "فعالیت"
    Proposal = "Proposal", "پروپوزال"
    Message = "Message", "پیام"
    Template = "Template", "قالب"
    ONE_ON_ONE = "OneOnOne", "یک‌به‌یک"
    FEEDBACK_REQUEST = "FeedbackRequest", "درخواست بازخورد"
    FEEDBACK = "Feedback", "بازخورد"

    @classmethod
    def default(cls):
        return cls.GOAL


class ProposalType(models.TextChoices):
    PROMOTION = "PROMOTION", "ارتقا"
    NOTICE = "NOTICE", "نوتیس"
    MAPPING = "MAPPING", "مپینگ اولیه"
    EVALUATION = "EVALUATION", "ارزیابی"

    @classmethod
    def default(cls):
        return cls.PROMOTION


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


committee_roles_permissions = {
    NoteType.Proposal: {
        "can_view": True,
        "can_edit": False,
        "can_view_summary": True,
        "can_write_summary": False,
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
    proposal_type = models.CharField(
        max_length=16,
        choices=ProposalType.choices,
        default=ProposalType.default,
        verbose_name="نوع پروپوزال",
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
    is_import = models.BooleanField(default=False, verbose_name="وارد شده از ایمپورت")
    _skip_access_grants = models.BooleanField(default=False, verbose_name="رد دسترسی‌های خودکار")

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


class Comment(MerlinBaseModel):
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
        verbose_name = "نظر"
        verbose_name_plural = "نظرها"

    def __str__(self):
        return f"{self.owner} - {self.note}"


class Summary(MerlinBaseModel):
    content = models.TextField(verbose_name="محتوا")
    note = models.OneToOneField(Note, on_delete=models.CASCADE, verbose_name="یادداشت")
    performance_label = models.CharField(
        max_length=256, default="", blank=True, null=True, verbose_name="لیبل عملکردی"
    )
    ladder = models.ForeignKey(
        "api.Ladder", null=True, blank=True, on_delete=models.PROTECT, verbose_name="لدر"
    )
    aspect_changes = models.JSONField(default=dict, blank=True, verbose_name="تغییرات ابعاد لدر")
    ladder_change = models.CharField(
        max_length=256,
        default="",
        blank=True,
        null=True,
        verbose_name="تغییر در سطح لدر",
    )
    bonus = models.IntegerField(default=0, verbose_name="پاداش عملکردی")
    salary_change = models.FloatField(default=0, verbose_name="تغییر پله‌ی حقوقی")
    seniority_level = models.CharField(
        max_length=20,
        choices=[
            ("JUNIOR", "Junior"),
            ("MID", "Mid"),
            ("SENIOR", "Senior"),
            ("PRINCIPAL", "Principal"),
        ],
        null=True,
        blank=True,
        verbose_name="سطح سنیوریتی",
        help_text="Optional seniority classification (Junior/Mid/Senior/Principal)",
    )
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
    is_import = models.BooleanField(default=False, verbose_name="وارد شده از ایمپورت")

    class Meta:
        verbose_name = "جمع‌بندی"
        verbose_name_plural = "جمع‌بندی‌ها"
        indexes = [
            models.Index(fields=["committee_date"]),
            models.Index(fields=["note", "committee_date"]),
        ]

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
    # Deprecated naming preserved for compatibility; still primary flag.
    can_write_feedback = models.BooleanField(default=False, verbose_name="نوشتن فیدبک")
    can_view_feedbacks = models.BooleanField(
        default=False, verbose_name="مشاهده نظرها"
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
        
        if note.type == NoteType.ONE_ON_ONE:
            return
        
        # FEEDBACK and FEEDBACK_REQUEST notes have explicit access control
        # managed by dedicated service functions (grant_feedback_access, grant_feedback_request_access)
        if note.type in [NoteType.FEEDBACK, NoteType.FEEDBACK_REQUEST]:
            return
        
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
        committee:Committee = note.owner.committee
        if committee is not None:
            # Committee role members
            if note.submit_status in (NoteSubmitStatus.PENDING, NoteSubmitStatus.REVIEWED) and note.type in committee_roles_permissions.keys():
                for member in note.owner.get_committee_role_members():
                    cls.objects.update_or_create(
                        user=member,
                        note=note,
                        defaults=committee_roles_permissions[note.type],
                    )
                for member in committee.members.all():
                    cls.objects.update_or_create(
                        user=member,
                        note=note,
                        defaults=committee_roles_permissions[note.type],
                    )


        # Mentioned users
        for user in note.mentioned_users.all():
            cls.objects.update_or_create(
                user=user,
                note=note,
                defaults={
                    "can_view": True,
                    "can_edit": False,
                    "can_view_summary": False,
                    "can_write_summary": False,
                    "can_view_feedbacks": False,
                    "can_write_feedback": True,
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

    personal_summary = models.CharField(null=True, blank=True)
    career_summary = models.CharField(null=True, blank=True)
    communication_summary = models.CharField(null=True, blank=True)    
    performance_summary = models.CharField(max_length=800)

    # Actions text
    actions = models.TextField(null=True, blank=True)

    # Vibes
    leader_vibe = models.CharField(max_length=2, choices=Vibe.choices)
    member_vibe = models.CharField(max_length=2, choices=Vibe.choices, null=True, blank=True)

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

# ────────────────────────────────────────────────────────────────
# Feedback feature models
# ----------------------------------------------------------------


class FeedbackForm(MerlinBaseModel):
    """Stores a predefined questionnaire for structured feedback."""

    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    schema = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "فرم بازخورد"
        verbose_name_plural = "فرم‌های بازخورد"

    def __str__(self):
        return self.title


class FeedbackRequest(MerlinBaseModel):
    """Extra metadata for a feedback request note (Note.type = FEEDBACK_REQUEST)."""

    note = models.OneToOneField("Note", on_delete=models.CASCADE, related_name="feedback_request")
    deadline = models.DateField(null=True, blank=True)
    form = models.ForeignKey(FeedbackForm, null=True, blank=True, on_delete=models.SET_NULL)
    is_public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "درخواست بازخورد"
        verbose_name_plural = "درخواست‌های بازخورد"

    def __str__(self):
        return f"Request • {self.note.title}"


class FeedbackRequestUserLink(models.Model):
    """Who was asked to give feedback and whether they answered."""

    request = models.ForeignKey(FeedbackRequest, on_delete=models.CASCADE, related_name="requestees")
    user = models.ForeignKey("api.User", on_delete=models.CASCADE)
    answered = models.BooleanField(default=False)

    class Meta:
        unique_together = ("request", "user")
        verbose_name = "لینک درخواست بازخورد"
        verbose_name_plural = "لینک‌های درخواست بازخورد"

    def __str__(self):
        return f"{self.request} → {self.user}"


class FeedbackTagLink(models.Model):
    feedback = models.ForeignKey("Feedback", on_delete=models.CASCADE)
    tag = models.ForeignKey(ValueTag, on_delete=models.CASCADE)
    section = models.CharField(max_length=32, choices=ValueSection.choices)

    class Meta:
        unique_together = ("feedback", "tag", "section")
        verbose_name = "تگ بازخورد"
        verbose_name_plural = "تگ‌های بازخورد"


class Feedback(MerlinBaseModel):
    """An actual feedback message (ad-hoc or answer to a request)."""

    note = models.OneToOneField("Note", on_delete=models.CASCADE, related_name="feedback")
    sender = models.ForeignKey("api.User", on_delete=models.CASCADE, related_name="sent_feedbacks")
    receiver = models.ForeignKey("api.User", on_delete=models.CASCADE, related_name="received_feedbacks")
    feedback_request = models.ForeignKey("FeedbackRequest", null=True, blank=True, on_delete=models.SET_NULL, related_name="feedback_answers")
    form = models.ForeignKey(FeedbackForm, null=True, blank=True, on_delete=models.SET_NULL)
    content = models.TextField()
    evidence = models.TextField(blank=True)
    cycle = models.ForeignKey(Cycle, on_delete=models.PROTECT)
    tags = models.ManyToManyField(ValueTag, through=FeedbackTagLink, related_name="feedback_tags")

    class Meta:
        verbose_name = "بازخورد"
        verbose_name_plural = "بازخوردها"
        ordering = ("-date_created",)
        db_table = "api_feedback_entry"

    def __str__(self):
        return f"Feedback • {self.sender} → {self.receiver}"