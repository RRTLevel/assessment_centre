from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import DomainUser, Note, Pack, Application, Category, InterviewResponse, Indicator
from .models import DomainUser, Note, Pack, Application, Category, InterviewResponse, Questions


ACCOUNT_TYPE_CHOICES = [
    ("Admin", "Admin"),
    ("Assessor", "Assessor"),
    ("Early Careers Definer", "Early Careers Definer (ECD)"),
    ("Early Careers Assessment Manager", "Early Careers Assessment Manager (ECAM)"),
]


class DomainUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control input"}),
    )

    account_type = forms.ChoiceField(
        choices=[("", "Select account type"), *ACCOUNT_TYPE_CHOICES],
        required=True,
        widget=forms.Select(attrs={"class": "form-control input"}),
    )

    class Meta:
        model = DomainUser
        fields = ("username", "email", "account_type", "password1", "password2")

    def clean_username(self):
        username = self.cleaned_data["username"]

        if DomainUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")

        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        account_type_name = self.cleaned_data["account_type"]

        if commit:
            user.save()
            group, _ = Group.objects.get_or_create(name=account_type_name)
            user.groups.add(group)

        return user


class DomainUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = DomainUser
        help_texts = {
            "username": _("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        }


class AddNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", "body")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control input",
                "placeholder": "Title"
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control input textarea pt-1",
                "placeholder": "Description...",
                "rows": 4
            }),
        }


class PackForm(forms.ModelForm):

    question_1 = forms.ModelChoiceField(
        queryset=Questions.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_1"})
    )

    question_2 = forms.ModelChoiceField(
        queryset=Questions.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_2"})
    )

    question_3 = forms.ModelChoiceField(
        queryset=Questions.objects.none(),
        required=False,
        widget=forms.Select(attrs={"id": "id_question_3"})
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        category_id = None

        if "category" in self.data:
            try:
                category_id = int(self.data.get("category"))
            except (TypeError, ValueError):
                category_id = None

        if category_id:
            qs = Questions.objects.filter(category_id=category_id)
        else:
            qs = Questions.objects.all()

        self.fields["question_1"].queryset = qs
        self.fields["question_2"].queryset = qs
        self.fields["question_3"].queryset = qs

class ApplicantForm(forms.Form):
    answer_1 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 1...'
        })
    )


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["answer_1", "answer_2", "answer_3"]
        widgets = {
            "answer_1": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 1"
            }),
            "answer_2": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 2"
            }),
            "answer_3": forms.Textarea(attrs={
                "class": "input",
                "placeholder": "Answer 3"
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class QuestionForm(forms.Form):
    question_1 = forms.CharField(widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))

    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "select"})
    )
    labels = {
            "text": "Enter your Question:",
            "category": "",
        }


class InterviewResponseForm(forms.ModelForm):
    class Meta:
        model = InterviewResponse
        fields = ["score_1", "score_2", "score_3", "notes", "feedback"]
        widgets = {
            "score_1": forms.NumberInput(attrs={"class": "score-input", "min": "1", "max": "6", "step": "1"}),
            "score_2": forms.NumberInput(attrs={"class": "score-input", "min": "1", "max": "6", "step": "1"}),
            "score_3": forms.NumberInput(attrs={"class": "score-input", "min": "1", "max": "6", "step": "1"}),
            "notes": forms.Textarea(attrs={
                "class": "notes-textarea",
                "placeholder": "Enter interview notes here...",
            }),
            "feedback": forms.Textarea(attrs={
                "class": "feedback-textarea",
                "placeholder": "Enter feedback here...",
            }),
        }


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = ["positive", "negative"]
 
class IndicatorPairForm(forms.Form):
    positive = forms.CharField(required=True)
    negative = forms.CharField(required=True)


class IndicatorPairForm(forms.Form):
    positive = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Positive indicator..."})
    )
    negative = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Negative indicator..."})
    )