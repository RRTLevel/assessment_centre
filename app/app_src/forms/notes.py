from django import forms

from ..models import Note


class AddNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("title", "body")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control input",
                "placeholder": "Title",
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control input textarea pt-1",
                "placeholder": "Description...",
                "rows": 4,
            }),
        }
