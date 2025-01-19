from django import forms
from .models import Response, Question

class FormResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Pass `questions` when initializing the form
        questions = kwargs.pop('question', [])
        super().__init__(*args, **kwargs)

        # Add Likert scale fields for each question
        for question in questions:
            self.fields[f"question_{question.id}"] = forms.ChoiceField(
                choices=[(None, "نمی‌دونم")] + [(i, str(i)) for i in range (question.scale_min, question.scale_max + 1)],
                required = False, 
                widget=forms.RadioSelect,
                label=question.question_text
            )

        # A single optional text box for each form
        self.fields['general_comment'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={"rows": 4, "placeholder": "اگه دوست داری می‌تونی نظرت رو بنویسی"}),
            label="Additional Comment",
        )
