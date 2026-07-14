"""Running interviews and the interview inbox/calendar."""

import calendar
import datetime
import json
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

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
