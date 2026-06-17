from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from .models import DomainUser, Note
from .models import Pack


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
        fields = ['title', 'description']