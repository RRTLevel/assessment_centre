from django import forms

from ..models import Application, Pack, Question


class PackForm(forms.ModelForm):
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
            "pre_interview_question_1",
            "pre_interview_question_2",
            "pre_interview_question_3",
            "question_1",
            "question_2",
            "question_3",
        ]

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
