"""The home dashboard, static pages and error pages."""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

from ..models import Application
from ..permissions import (
    ASSESSOR_GROUP,
    ECAM_GROUP,
    ECD_GROUP,
    has_any_group,
    is_admin_user,
)


class HomeView(LoginRequiredMixin, TemplateView):
    """Landing dashboard: application stats and shortcuts for staff, the
    submission status for candidates."""

    template_name = "home/home.html"

    RECENT_LIMIT = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = settings.APPLICATION_NAME + " - Home"

        user = self.request.user
        can_review = is_admin_user(user) or has_any_group(user, {ECD_GROUP, ECAM_GROUP})
        context["is_staff"] = can_review or has_any_group(user, {ASSESSOR_GROUP})

        status_filter = self.request.GET.get("status", "")
        if status_filter not in dict(Application.STATUS_CHOICES):
            status_filter = ""
        context["status_filter"] = status_filter

        if can_review:
            context.update(self._application_stats(status_filter))
        elif not context["is_staff"]:
            context["my_application"] = (
                Application.objects.filter(user=user)
                .select_related("pack", "group")
                .order_by("-created_at")
                .first()
            )

        return context

    def _application_stats(self, status_filter=""):
        # A group submission is one Application row per pack, all sharing an
        # application_id, so submissions are counted by distinct id.
        def submission_count(queryset):
            return queryset.values("application_id").distinct().count()

        applications = Application.objects.all()

        recent_qs = applications
        if status_filter:
            recent_qs = recent_qs.filter(status=status_filter)

        recent = []
        seen_ids = set()
        for application in recent_qs.select_related("user", "pack", "group").order_by("-created_at"):
            if application.application_id in seen_ids:
                continue
            seen_ids.add(application.application_id)
            recent.append(application)
            if len(recent) == self.RECENT_LIMIT:
                break

        return {
            "pending_count": submission_count(
                applications.filter(status=Application.STATUS_PENDING)
            ),
            "accepted_count": submission_count(
                applications.filter(status=Application.STATUS_ACCEPTED)
            ),
            "upcoming_count": submission_count(
                applications.filter(
                    status=Application.STATUS_ACCEPTED,
                    interview_date__gte=timezone.now(),
                )
            ),
            "recent_applications": recent,
        }


def documentation_view(request):
    return render(request, "notes/documentation.html")


def help_view(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"
