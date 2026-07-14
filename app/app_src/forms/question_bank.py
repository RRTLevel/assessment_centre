from django import forms
from django.utils.html import strip_tags

from ..models import Category


def has_visible_text(html):
    """True when rich text HTML contains something other than empty markup."""
    return bool(strip_tags(html).replace("&nbsp;", " ").strip())


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

    def clean_description(self):
        """Treat editor leftovers like "<p><br></p>" as an empty description."""
        description = self.cleaned_data.get("description", "")
        return description if has_visible_text(description) else ""


class QuestionForm(forms.Form):
    """Add up to five questions to a category in one submission."""

    QUESTION_COUNT = 5

    # "richtext" textareas are replaced by the Summernote editor. All fields are
    # optional at field level (the hidden originals must not trip browser
    # validation); "at least one question" is enforced in question_texts().
    question_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))

    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    def clean(self):
        """At least one question is required (fields are individually optional
        so the editor-hidden originals don't trip browser validation)."""
        cleaned = super().clean()
        if not self.question_texts():
            raise forms.ValidationError("Please enter at least one question.")
        return cleaned

    def question_texts(self):
        """Return the non-empty question texts that were submitted.

        The editor submits HTML, so blank entries like "<p><br></p>" are skipped.
        """
        return [
            text.strip()
            for i in range(1, self.QUESTION_COUNT + 1)
            if (text := self.cleaned_data.get(f"question_{i}")) and has_visible_text(text)
        ]
