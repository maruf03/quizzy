from django import forms
from django.forms import inlineformset_factory

from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "allow_multiple_attempts", "max_attempts"]


class BaseAnswerFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        total = 0
        has_correct = False
        for form in self.forms:
            if getattr(form, "cleaned_data", None) and not form.cleaned_data.get("DELETE"):
                text = form.cleaned_data.get("text")
                if text:
                    total += 1
                    if form.cleaned_data.get("is_correct"):
                        has_correct = True
        if total < 2:
            raise forms.ValidationError("Provide at least two answers")
        if not has_correct:
            raise forms.ValidationError("Mark at least one answer as correct")


AnswerFormSet = inlineformset_factory(
    Question,
    Answer,
    fields=["text", "is_correct"],
    extra=3,
    can_delete=True,
    formset=BaseAnswerFormSet,
)
