"""Running interviews and the interview inbox/calendar."""

import datetime
import calendar
from collections import defaultdict

from django.utils import timezone
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect

from ..models import Question

from ..models import Application, Category, Question
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.interviews import interview_context, save_interview_submission
from django.shortcuts import render, get_object_or_404


from ..models import Application, Question


from ..models import Application, Question



@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def start_interview(request, application_id):

    applications = Application.objects.filter(
        application_id=application_id
    ).select_related(
        "user",
        "group",
        "pack"
    )

    if not applications.exists():
        return render(
            request,
            "pre_interview/no_application.html"
        )

    application = applications.first()

    questions = Question.objects.all()

    question_data = []

    for app in applications:
        for question in questions:
            question_data.append({
                "question": question,
                "application": app,
            })


    print("QUESTIONS FOUND:", questions.count())
    print("QUESTION DATA:", len(question_data))


    return render(
        request,
        "pre_interview/start_interview.html",
        {
            "application": application,
            "applications": applications,
            "question_data": question_data,
        }
    )

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def inbox_view(request):
    today = datetime.date.today()
    year, month = _requested_month(request, today)
    now = timezone.now()

    # -------------------------
    # UPCOMING (leave as-is)
    # -------------------------
    upcoming_interviews = (
        Application.objects
        .filter(interview_date__gte=now)
        .select_related("user", "pack", "group")
        .order_by("interview_date")
    )

    # -------------------------
    # PAST → GROUPED FIX
    # -------------------------
    past_apps = (
        Application.objects
        .filter(interview_date__lt=now)
        .select_related("user", "pack", "group")
        .prefetch_related("results__question")
        .order_by("-interview_date")
    )

    grouped = defaultdict(list)

    for app in past_apps:
        group_name = app.pack.group_name or "No Group"
        key = (app.user_id, group_name)
        grouped[key].append(app)

    past_interviews = []

    for (user_id, group_id), apps in grouped.items():
        user = apps[0].user
        group = apps[0].group

        all_results = []
        scores = []

        for app in apps:
            results = list(app.results.all())
            all_results.extend(results)

            scores.extend([
                r.score for r in results
                if r.score is not None
            ])

        avg_score = round(sum(scores) / len(scores), 2) if scores else None

        past_interviews.append({
            "user": user,
            "group": group,
            "applications": apps,
            "results": all_results,
            "avg_score": avg_score,
            "date": max(
                (a.interview_date for a in apps if a.interview_date),
                default=None
            ),
        })

    # -------------------------
    # CALENDAR (unchanged)
    # -------------------------
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
