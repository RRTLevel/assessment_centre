from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import DomainUser, Note
from .models import Pack


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
            "class": "form-control input",
        }),
    )
    account_type = forms.ChoiceField(
        choices=[("", "Select account type"), *ACCOUNT_TYPE_CHOICES],
        required=True,
        widget=forms.Select(attrs={
            "class": "form-control input",
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
            account_type, _ = Group.objects.get_or_create(name=account_type_name)
            user.groups.add(account_type)

        return user
    
class DomainUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):

        model = DomainUser
        help_texts = {
            'username': _('Required. 150 characters or fewer. Letters, digits and \/@/./+/-/_ only.'),
        }


class AddNoteForm(forms.ModelForm):

    class Meta:
        model = Note

        fields = ('title', 'body')

        widgets = {
            'title': forms.TextInput(attrs={
                'required': True,
                'class': "form-control input",
                'placeholder': 'Title'
            }),
            'body': forms.Textarea(attrs={
                'required': True,
                'class': "form-control input textarea pt-1",
                'placeholder': 'Description...',
                'rows': 4
            }),
        }

class PackForm(forms.ModelForm):
    class Meta:
        model = Pack
        fields = [
            'title',
            'description',
            'pack_class', 
            'pre_interview_question_1',
            'pre_interview_question_2',
            'pre_interview_question_3',
        ]
        
class ApplicantForm(forms.Form):
    answer_1 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 1...'
        })
    )

    answer_2 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 2...'
        })
    )

    answer_3 = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'textarea',
            'placeholder': 'Your answer to question 3...'
        })
    )