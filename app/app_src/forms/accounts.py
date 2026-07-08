from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from ..models import DomainUser
from ..permissions import ADMIN_GROUP, ASSESSOR_GROUP, ECAM_GROUP, ECD_GROUP

ACCOUNT_TYPE_CHOICES = [
    (ADMIN_GROUP, "Admin"),
    (ASSESSOR_GROUP, "Assessor"),
    (ECD_GROUP, "Early Careers Definer (ECD)"),
    (ECAM_GROUP, "Early Careers Assessment Manager (ECAM)"),
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
            group, _created = Group.objects.get_or_create(name=account_type_name)
            user.groups.add(group)

        return user


class DomainUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = DomainUser
        help_texts = {
            "username": _("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        }
