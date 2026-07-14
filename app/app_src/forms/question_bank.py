
from django import forms
from ..models import Category
from app_src.models import Pack



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]



class QuestionForm(forms.Form):
    QUESTION_COUNT = 5

    question_1 = forms.CharField(widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_2 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_3 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_4 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))
    question_5 = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "textarea", "rows": 3}))

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    pack = forms.ModelChoiceField(
        required=False,
        queryset=Pack.objects.all(),
        widget=forms.Select(attrs={"class": "select"}),
    )

    def question_texts(self):
        return [
            text.strip()
            for i in range(1, self.QUESTION_COUNT + 1)
            if (text := self.cleaned_data.get(f"question_{i}")) and text.strip()
        ]