"""Running interviews and the interview inbox/calendar."""

import calendar
import datetime
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from ..models import Application
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.interviews import (
    get_interview_packs,
    interview_context,
    save_interview_submission,
)
from .applications import submission_rows


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def start_interview(request, application_id):
    """The interview page for one submission: every chosen pack's questions
    plus the interview-level indicator assessment."""
    rows = submission_rows(application_id)
    if not rows:
        raise Http404("No application with this id.")
    application = rows[0]

    interview_packs = get_interview_packs(application, rows)

    if request.method == "POST":
        save_interview_submission(application, interview_packs, request.POST)
        messages.success(request, f"Interview for {application.user.username} submitted.")
        return redirect("inbox")

    context = interview_context(application, interview_packs)
    context.update({
        "application": application,
        "group_applications": rows,
    })
    return render(request, "pre_interview/start_interview.html", context)


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def autosave_interview(request, application_id):
    """Background save for the interview page; same fields as the submit."""
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    rows = submission_rows(application_id)
    if not rows:
        return JsonResponse({"ok": False}, status=404)
    application = rows[0]

    interview_packs = get_interview_packs(application, rows)
    save_interview_submission(application, interview_packs, request.POST)

    return JsonResponse({"ok": True})


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def inbox_view(request):
    today = datetime.date.today()
    year, month = _requested_month(request, today)
    now = timezone.now()

    upcoming_interviews = _grouped_interviews(
        Application.objects
        .filter(interview_date__gte=now)
        .select_related("user", "pack", "group")
        .order_by("interview_date", "id")
    )

    past_interviews = _grouped_interviews(
        Application.objects
        .filter(interview_date__lt=now)
        .select_related("user", "pack", "group")
        .prefetch_related("results__question", "results__application_pack__pack")
        .order_by("-interview_date", "id")
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
        "today_day": today.day if today.month == month and today.year == year else None,
        "marked_days": marked_days,
        "upcoming_interviews": upcoming_interviews,
        "past_interviews": past_interviews,
        **_month_navigation(year, month),
        "applications": True,
    })


def _grouped_interviews(applications):
    """Collapse Application rows into one entry per submission.

    Results and the average score live on the submission's primary (first)
    application row.
    """
    grouped = defaultdict(list)
    for application in applications:
        grouped[application.application_id].append(application)

    entries = []
    for rows in grouped.values():
        primary = min(rows, key=lambda row: row.id)

        entries.append({
            "application": primary,
            "user": primary.user,
            "group": primary.group,
            "packs": [row.pack for row in rows],
            "rows": rows,
            "results": list(primary.results.all()),
            "interview_date": primary.interview_date,
            "average_score": primary.average_score,
        })

    return entries


def _requested_month(request, today):
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
