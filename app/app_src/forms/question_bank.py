from django import forms
from django.utils.html import strip_tags

from ..models import Category, Genre, Pack


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
    QUESTION_COUNT = 5

    # "richtext" textareas are replaced by the Summernote editor. All fields are
    # optional at field level (the hidden originals must not trip browser
    # validation); "at least one question" is enforced in clean().
    question_1 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))
    question_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea richtext", "rows": 3}))

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    def clean(self):
        """At least one question is required."""
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


_pack_select = {"class": "select", "style": "width:100%;"}


class GenreForm(forms.ModelForm):
    """Create or edit a Genre (a named grouping of exactly 3 packs)."""

    pack_1 = forms.ModelChoiceField(
        required=False,
        queryset=Pack.objects.all(),
        empty_label="— Select pack 1 —",
        widget=forms.Select(attrs=_pack_select),
    )
    pack_2 = forms.ModelChoiceField(
        required=False,
        queryset=Pack.objects.all(),
        empty_label="— Select pack 2 —",
        widget=forms.Select(attrs=_pack_select),
    )
    pack_3 = forms.ModelChoiceField(
        required=False,
        queryset=Pack.objects.all(),
        empty_label="— Select pack 3 —",
        widget=forms.Select(attrs=_pack_select),
    )

    class Meta:
        model = Genre
        fields = ["name", "pack_1", "pack_2", "pack_3"]
        widgets = {"name": forms.TextInput(attrs={"class": "input"})}
