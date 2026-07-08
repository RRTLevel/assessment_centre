"""Login, signup, profile and account management."""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from ..forms import DomainUserCreationForm


class RememberMeLoginView(LoginView):
    template_name = "registration/login.html"
    REMEMBER_ME_AGE = 60 * 60 * 24 * 30

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.POST.get("remember_me"):
            self.request.session.set_expiry(self.REMEMBER_ME_AGE)
        else:
            self.request.session.set_expiry(0)

        return super().form_valid(form)


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = DomainUserCreationForm
    success_url = reverse_lazy("login")
    success_message = "Your account has been created!"
    template_name = "registration/signup.html"


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = "notes/userprofile.html"

    MIN_PASSWORD_LENGTH = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = settings.APPLICATION_NAME + " - Profile"
        context["AccountType"] = self.request.user.groups.first()
        return context

    def post(self, request, **kwargs):
        user = request.user
        old_pass = request.POST.get("old_password")
        new_pass1 = request.POST.get("new_password1")
        new_pass2 = request.POST.get("new_password2")

        if not user.check_password(old_pass):
            messages.error(request, "Incorrect current password.")
            return redirect("userprofile")

        if new_pass1 != new_pass2:
            messages.error(request, "Passwords do not match.")
            return redirect("userprofile")

        if len(new_pass1) < self.MIN_PASSWORD_LENGTH:
            messages.error(request, "Password too short.")
            return redirect("userprofile")

        user.set_password(new_pass1)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated.")
        return redirect("userprofile")


class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request):
        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(request, "Incorrect password.")
            return redirect("userprofile")

        user = request.user
        logout(request)
        user.delete()
        return redirect("/")
