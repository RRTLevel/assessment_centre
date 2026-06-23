from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

<<<<<<< Updated upstream
from .models import DomainUser, Note
from .models import Pack
from .models import Category
=======
from .models import DomainUser, Note, Pack, Application
>>>>>>> Stashed changes


ACCOUNT_TYPE_CHOICES = [
    ("Admin", "Admin"),
    ("Assessor", "Assessor"),
    ("Early Careers Definer", "Early Careers Definer (ECD)"),
    ("Early Careers Assessment Manager", "Early Careers Assessment Manager (ECAM)"),
]


class DomainUserCreationForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "input",
        }),
    )

    account_type = forms.ChoiceField(
        choices=[("", "Select account type"), *ACCOUNT_TYPE_CHOICES],
        required=True,
        widget=forms.Select(attrs={
            "class": "input",
        }),
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
            'username': _('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        }


class AddNoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ('title', 'body')

        widgets = {
            'title': forms.TextInput(attrs={
                'class': "input rr-primary",
                'placeholder': 'Title'
            }),
            'body': forms.Textarea(attrs={
                'class': "input rr-primary textarea",
                'placeholder': 'Description...',
                'rows': 4
            }),
        }


class PackForm(forms.ModelForm):

    class Meta:
        model = Pack
<<<<<<< Updated upstream
        fields = [
            "title",
            "description",
            "category",
            "pre_interview_question_1",
            "pre_interview_question_2",
            "pre_interview_question_3",
        ]
        
class ApplicantForm(forms.Form):
    answer_1 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 1...'
        })
    )
=======
        fields = ['title', 'description']
>>>>>>> Stashed changes


<<<<<<< Updated upstream
    answer_3 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 3...'
        })
    )


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
=======

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
>>>>>>> Stashed changes
