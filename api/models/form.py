from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.models.base import MerlinBaseModel
from api.models.user import User
from api.models.cycle import Cycle

__all__ = ['Form', 'Question', 'FormResponse', 'FormAssignment']

class Form(MerlinBaseModel):
    class FormType(models.TextChoices):
        PM = "PM", "Product Manager"
        TL = "TL", "Team Leader"
        MANAGER = "MANAGER", "Manager"
        GENERAL = "GENERAL", "General"

    name = models.CharField(max_length=256, verbose_name="نام")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    is_default = models.BooleanField(verbose_name="فرم پیش‌فرض")
    form_type = models.CharField(
        max_length=20,
        choices=FormType.choices,
        verbose_name="نوع فرم",
        null=True,
        blank=True
    )
    cycle = models.ForeignKey(Cycle, on_delete=models.PROTECT, verbose_name="دوره")     # FUTURE ENHANCEMENT: In order to decouple the forms from cycles, cycle should be moved to FormResponse model.

    class Meta:
        verbose_name = "فرم"
        verbose_name_plural = "فرم‌ها"

    def __str__(self):
        return self.name

class Question(MerlinBaseModel):
    question_text = models.TextField(verbose_name="متن سوال")
    scale_min = models.PositiveIntegerField(default=1, verbose_name="حداقل امتیاز")
    scale_max = models.PositiveIntegerField(default=5, verbose_name="حداکثر امتیاز")
    category = models.CharField(
        max_length=100,
        verbose_name="دسته‌بندی"
    )
    form = models.ForeignKey(Form, on_delete=models.PROTECT, verbose_name="فرم")

    class Meta:
        verbose_name = "سوال"
        verbose_name_plural = "سوال‌ها"

    def __str__(self):
        return f"{self.question_text} ({self.category})"

class FormResponse(MerlinBaseModel):
    answer = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="امتیاز")   # null represents "I don't know"
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="کاربر")
    form = models.ForeignKey(Form, on_delete=models.PROTECT, verbose_name="فرم")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, verbose_name="سوال")

    class Meta:
        verbose_name = "پاسخ"
        verbose_name_plural = "پاسخ‌ها"
        unique_together = ("user", "form", "question")

    def __str__(self):
        return f"Response by {self.user} to {self.question}"

    def get_answer_display(self):
        # Ensure that None will be displayed as "I don't know"
        return self.answer if self.answer is not None else "I don't know"


    def clean(self):
        if self.answer is not None:
            if not self.question.scale_min <= self.answer <= self.question.scale_max:
                raise ValidationError({
                    'answer': f"The answer must be between {self.question.scale_min} and {self.question.scale_max}."
                })

class FormAssignment(MerlinBaseModel):
    form = models.ForeignKey(Form, on_delete=models.PROTECT, verbose_name="فرم")
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assigned_forms", verbose_name="گیرنده")
    assigned_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_assignments", verbose_name="فرستنده")
    message = models.TextField(null=True, blank=True, verbose_name="پیام")
    deadline = models.DateField(verbose_name="ددلاین")
    is_completed = models.BooleanField(default=False, verbose_name="تکمیل‌شده")

    def __str__(self):
        return f"{self.form.name} assigned to {self.assigned_to}"

