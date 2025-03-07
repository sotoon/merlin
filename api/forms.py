from django import forms

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

