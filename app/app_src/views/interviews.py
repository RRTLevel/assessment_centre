"""Running interviews and the interview inbox/calendar."""

import datetime
import calendar
from collections import defaultdict

import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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

from ..models import (
    Application,
    ApplicationPack,
    Indicator,
    IndicatorGroupScore,
    IndicatorScore,
    InterviewResult,
    Questions,
)
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required


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
    application = get_object_or_404(Application, application_id=application_id)

    interview_packs = list(application.interview_packs.select_related("pack__category").order_by("order"))
    if not interview_packs:
        ap, _ = ApplicationPack.objects.get_or_create(
            application=application, pack=application.pack, defaults={"order": 0}
        )
        interview_packs = [ap]

    if request.method == "POST":
        overall_scores = []

        for ap in interview_packs:
            questions = Questions.objects.filter(category=ap.pack.category)
            for question in questions:
                notes = request.POST.get(f"notes_{ap.id}_{question.id}", "")
                feedback = request.POST.get(f"feedback_{ap.id}_{question.id}", "")
                overall_score_raw = request.POST.get(f"overall_score_{ap.id}_{question.id}")
                overall_score = int(overall_score_raw) if overall_score_raw and overall_score_raw.isdigit() else None
                if overall_score is not None:
                    overall_scores.append(overall_score)
                InterviewResult.objects.update_or_create(
                    application=application,
                    question=question,
                    defaults={"score": overall_score, "notes": notes, "feedback": feedback, "application_pack": ap},
                )

        for key, value in request.POST.items():
            m = re.match(r"^indicator_score_(\d+)$", key)
            if m and value and value.isdigit():
                try:
                    indicator = Indicator.objects.get(id=int(m.group(1)))
                    IndicatorScore.objects.update_or_create(
                        application=application,
                        indicator=indicator,
                        defaults={"score": int(value)},
                    )
                except Indicator.DoesNotExist:
                    pass

            if key.startswith("group_score_") and value and value.isdigit():
                group_name = key[len("group_score_"):]
                if group_name:
                    IndicatorGroupScore.objects.update_or_create(
                        application=application,
                        group_name=group_name,
                        defaults={"score": int(value), "notes": request.POST.get(f"group_notes_{group_name}", "")},
                    )

        application.average_score = round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else None
        application.save()
        messages.success(request, f"Interview for {application.user.username} submitted.")
        return redirect("inbox")

    saved = {result.question_id: result for result in application.results.all()}
    pack_data = []
    total_questions = 0
    for ap in interview_packs:
        questions = list(Questions.objects.filter(category=ap.pack.category))
        total_questions += len(questions)
        pack_data.append({
            "ap": ap,
            "pack": ap.pack,
            "question_data": [{"question": q, "result": saved.get(q.id)} for q in questions],
        })

    saved_indicator_scores = {s.indicator_id: s.score for s in application.indicator_scores.all()}
    saved_group_scores = {}
    saved_group_notes = {}
    for s in application.indicator_group_scores.all():
        saved_group_scores[s.group_name] = s.score
        saved_group_notes[s.group_name] = s.notes

    indicator_groups = {}
    for ind in Indicator.objects.order_by("name", "id"):
        indicator_groups.setdefault(ind.name, []).append({
            "id": ind.id, "positive": ind.positive, "negative": ind.negative,
        })

    return render(request, "pre_interview/start_interview.html", {
        "application": application,
        "pack_data": pack_data,
        "total_questions": total_questions,
        "indicator_groups_json": json.dumps(indicator_groups),
        "saved_indicator_scores_json": json.dumps(saved_indicator_scores),
        "saved_group_scores_json": json.dumps(saved_group_scores),
        "saved_group_notes_json": json.dumps(saved_group_notes),
    })

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
def autosave_interview(request, application_id):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)

    application = get_object_or_404(Application, application_id=application_id)
    interview_packs = list(application.interview_packs.select_related("pack__category").order_by("order"))
    if not interview_packs:
        ap, _ = ApplicationPack.objects.get_or_create(
            application=application, pack=application.pack, defaults={"order": 0}
        )
        interview_packs = [ap]

    overall_scores = []
    for ap in interview_packs:
        questions = Questions.objects.filter(category=ap.pack.category)
        for question in questions:
            notes = request.POST.get(f"notes_{ap.id}_{question.id}", "")
            feedback = request.POST.get(f"feedback_{ap.id}_{question.id}", "")
            overall_score_raw = request.POST.get(f"overall_score_{ap.id}_{question.id}")
            overall_score = int(overall_score_raw) if overall_score_raw and overall_score_raw.isdigit() else None
            if overall_score is not None:
                overall_scores.append(overall_score)
            InterviewResult.objects.update_or_create(
                application=application,
                question=question,
                defaults={"score": overall_score, "notes": notes, "feedback": feedback, "application_pack": ap},
            )

    for key, value in request.POST.items():
        m = re.match(r"^indicator_score_(\d+)$", key)
        if m and value and value.isdigit():
            try:
                indicator = Indicator.objects.get(id=int(m.group(1)))
                IndicatorScore.objects.update_or_create(
                    application=application,
                    indicator=indicator,
                    defaults={"score": int(value)},
                )
            except Indicator.DoesNotExist:
                pass

        if key.startswith("group_score_") and value and value.isdigit():
            group_name = key[len("group_score_"):]
            if group_name:
                IndicatorGroupScore.objects.update_or_create(
                    application=application,
                    group_name=group_name,
                    defaults={"score": int(value), "notes": request.POST.get(f"group_notes_{group_name}", "")},
                )

    if overall_scores:
        application.average_score = round(sum(overall_scores) / len(overall_scores), 2)
        application.save()

    return JsonResponse({"ok": True})


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
