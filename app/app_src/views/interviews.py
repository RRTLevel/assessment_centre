"""Running interviews and the interview inbox/calendar."""

import calendar
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..models import Application, Questions
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.interviews import interview_context, save_interview_submission


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def start_interview(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)
    questions = Questions.objects.filter(category=application.pack.category)

    if request.method == "POST":
        save_interview_submission(application, questions, request.POST)
        messages.success(request, f"Interview for {application.user.username} submitted.")
        return redirect("inbox")

    return render(request, "pre_interview/start_interview.html", {
        "application": application,
        **interview_context(application, questions),
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def inbox_view(request):
    today = datetime.date.today()
    year, month = _requested_month(request, today)
    now = timezone.now()

    upcoming_interviews = (
        Application.objects.filter(interview_date__gte=now)
        .select_related("user", "pack")
        .prefetch_related("results__question")
        .order_by("interview_date")
    )

    past_interviews = (
        Application.objects.filter(interview_date__lt=now)
        .annotate(avg_score=Avg("results__score"))
        .select_related("user", "pack")
        .prefetch_related("results__question")
        .order_by("-interview_date")
    )

    month_interviews = Application.objects.filter(
        interview_date__year=year,
        interview_date__month=month,
    )
    marked_days = {
        application.interview_date.day
        for application in month_interviews
        if application.interview_date
    }

    cal = calendar.Calendar(firstweekday=6)

    return render(request, "pre_interview/inbox.html", {
        "month_days": cal.monthdayscalendar(year, month),
        "month_name": calendar.month_name[month],
        "year": year,
        "today_day": today.day if today.month == month else None,
        "marked_days": marked_days,
        "upcoming_interviews": upcoming_interviews,
        "past_interviews": past_interviews,
        **_month_navigation(year, month),
        "applications": True,
    })


def _requested_month(request, today):
    """The (year, month) picked via query params, defaulting to this month."""
    year_param = request.GET.get("year")
    month_param = request.GET.get("month")

    year = int(year_param) if year_param and year_param.isdigit() else today.year
    month = int(month_param) if month_param and month_param.isdigit() else today.month

    if month < 1 or month > 12:
        month = today.month

    return year, month


def _month_navigation(year, month):
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return {
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    }
