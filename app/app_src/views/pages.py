"""Homepage, static pages and error pages."""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from ..models import Application
from ..permissions import ECD_GROUP, ECAM_GROUP, has_any_group, is_admin_user


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = True
        context["page_title"] = settings.APPLICATION_NAME + " - Home"

        user = self.request.user
        is_staff = is_admin_user(user) or has_any_group(user, {ECD_GROUP, ECAM_GROUP})

        now = timezone.now()
        if is_staff:
            context["pending_count"] = Application.objects.filter(status=Application.STATUS_PENDING).count()
            context["accepted_count"] = Application.objects.filter(status=Application.STATUS_ACCEPTED).count()
            context["upcoming_count"] = Application.objects.filter(
                interview_date__gte=now, status=Application.STATUS_ACCEPTED
            ).count()
            context["recent_applications"] = (
                Application.objects.select_related("user", "pack").order_by("-pk")[:5]
            )
        else:
            context["my_application"] = (
                Application.objects.filter(user=user).select_related("pack").order_by("-pk").first()
            )
        context["is_staff"] = is_staff
        return context


def documentation_view(request):
    return render(request, "notes/documentation.html")


def help_view(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"
