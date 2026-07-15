from django import forms

from ..models import Application, Pack, Question
from .question_bank import has_visible_text


class PackForm(forms.ModelForm):
    # Convenience pickers: selecting a bank question copies its text into the
    # matching pre-interview question editor (see the create-pack page script).
    question_1 = forms.ModelChoiceField(
        queryset=Question.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_1"}),
    )

    question_2 = forms.ModelChoiceField(
        queryset=Question.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_2"}),
    )

    question_3 = forms.ModelChoiceField(
        queryset=Question.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_3"}),
    )

    class Meta:
        model = Pack
        fields = [
            "title",
            "description",
            "category",
            "pre_interview_question_1",
            "pre_interview_question_2",
            "pre_interview_question_3",
            "question_1",
            "question_2",
            "question_3",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input"}),
            "pre_interview_question_1": forms.TextInput(attrs={"class": "input"}),
            "pre_interview_question_2": forms.TextInput(attrs={"class": "input"}),
            "pre_interview_question_3": forms.TextInput(attrs={"class": "input"}),
        # "richtext" textareas are replaced by the Summernote editor.
        widgets = {
            "description": forms.Textarea(attrs={"class": "textarea richtext", "rows": 4}),
            "pre_interview_question_1": forms.Textarea(attrs={"class": "textarea richtext", "rows": 2}),
            "pre_interview_question_2": forms.Textarea(attrs={"class": "textarea richtext", "rows": 2}),
            "pre_interview_question_3": forms.Textarea(attrs={"class": "textarea richtext", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        category_id = None

        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
            except (TypeError, ValueError):
                category_id = None

        if category_id:
            questions = Question.objects.filter(category_id=category_id)
        else:
            questions = Question.objects.all()

        self.fields["question_1"].queryset = questions
        self.fields["question_2"].queryset = questions
        self.fields["question_3"].queryset = questions

    def _clean_richtext(self, field_name):
        """Blank out editor leftovers like "<p><br></p>" for optional fields."""
        value = self.cleaned_data.get(field_name, "")
        return value if has_visible_text(value) else ""

    def clean_pre_interview_question_1(self):
        return self._clean_richtext("pre_interview_question_1")

    def clean_pre_interview_question_2(self):
        return self._clean_richtext("pre_interview_question_2")

    def clean_pre_interview_question_3(self):
        return self._clean_richtext("pre_interview_question_3")


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["answer_1", "answer_2", "answer_3"]
        widgets = {
            "answer_1": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 1",
            }),
            "answer_2": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 2",
            }),
            "answer_3": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 3",
            }),
        }
