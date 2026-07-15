from django import forms

from ..models import Category, Genre, Pack


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]


class QuestionForm(forms.Form):
    """Add up to five questions to a category in one submission."""

    QUESTION_COUNT = 5

    question_1 = forms.CharField(widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))

    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    def question_texts(self):
        """Return the non-empty question texts that were submitted."""
        return [
            text.strip()
            for i in range(1, self.QUESTION_COUNT + 1)
            if (text := self.cleaned_data.get(f"question_{i}")) and text.strip()
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
