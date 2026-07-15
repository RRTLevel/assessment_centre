"""Query logic behind the results page, candidate dashboard and PDF export."""

from django.contrib.auth.models import User
from django.db.models import Avg, Prefetch
from django.db.models.functions import ExtractYear
from django.db.models import Prefetch

from ..models import Application, IndicatorScore, InterviewResult, Question


def interview_results_by_candidate():
    """One entry per interviewed submission, newest first.


def available_years():
    """Distinct years in which applications were created, newest first."""
    return list(
        Application.objects
        .annotate(year=ExtractYear("created_at"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )


def candidate_dashboard_data(date_from=None, date_to=None, sort=None, year=None):
    """Build the dashboard heatmap: one row per interviewed candidate.

    Returns ``(questions, rows, col_avgs)`` where each row has the candidate's
    name, latest application, per-question scores (aligned with ``questions``)
    and their average score. ``col_avgs`` is one average per question column
    across all shown rows.
    Results, notes and feedback are organised by the packs they were scored
    under, alongside the interview's indicator scores — everything the
    results page shows for one candidate's group application.
    """
    applications = (
        Application.objects
        .filter(results__isnull=False)
        .distinct()
        .select_related("user", "group", "pack")
        .prefetch_related(
            Prefetch(
                "results",
                queryset=(
                    InterviewResult.objects
                    .select_related("question", "application_pack__pack")
                    .order_by("application_pack__order", "question_id")
                ),
            ),
            Prefetch(
                "indicator_scores",
                queryset=IndicatorScore.objects.select_related("indicator"),
            ),
            "indicator_group_scores",
        )
        .order_by("-created_at")
    )

    if year:
        users = users.filter(application__created_at__year=year)

    if date_from:
        users = users.filter(application__created_at__date__gte=date_from)
    entries = []
    for application in applications:
        packs = {}
        for result in application.results.all():
            pack = result.application_pack.pack if result.application_pack else application.pack
            packs.setdefault(pack, []).append(result)

        indicator_scores = {}
        for score in application.indicator_scores.all():
            indicator_scores.setdefault(score.indicator.name, []).append(score)

        entries.append({
            "application": application,
            "group": application.group,
            "pack_results": [
                {"pack": pack, "results": results}
                for pack, results in packs.items()
            ],
            "indicator_scores": indicator_scores,
            "indicator_group_scores": list(application.indicator_group_scores.all()),
        })

    return entries


def candidate_dashboard_data(date_from=None, date_to=None, sort=None):
    """Build the dashboard heatmap: one row per interviewed submission.

    Each row combines the results recorded across all packs of one group
    application, keyed by question for the heatmap columns.
    """
    questions = list(Question.objects.order_by("id"))

    applications = (
        Application.objects
        .filter(results__isnull=False)
        .distinct()
        .select_related("user", "group", "pack")
        .prefetch_related(
            Prefetch(
                "results",
                queryset=InterviewResult.objects.select_related("question").order_by("question_id"),
            )
        )
    )

    if date_from:
        applications = applications.filter(created_at__date__gte=date_from)

    if date_to:
        applications = applications.filter(created_at__date__lte=date_to)

    rows = []
    for application in applications:
        scores = {}
        all_scores = []

        for result in application.results.all():
            if result.score is not None:
                scores[result.question_id] = result.score
                all_scores.append(result.score)

        avg = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

        rows.append({
            "name": application.user.username,
            "group": application.group.name if application.group else application.pack.title,
            "date": application.created_at,
            "cells": [scores.get(question.id) for question in questions],
            "avg": avg,
            "application": application,
        })

    # Per-column averages across all shown rows (#28)
    col_avgs = []
    for i in range(len(questions)):
        scores = [r["cells"][i] for r in rows if r["cells"][i] is not None]
        col_avgs.append(round(sum(scores) / len(scores), 1) if scores else None)

    return questions, rows, col_avgs
    def avg_key(row):
        return row["avg"] if row["avg"] is not None else 0

    if sort == "lowest":
        # Unscored rows (avg None) always sort last.
        rows.sort(key=lambda r: (r["avg"] is None, avg_key(r)))
    elif sort == "newest":
        rows.sort(key=lambda r: r["date"], reverse=True)
    elif sort == "oldest":
        rows.sort(key=lambda r: r["date"])
    else:  # default = highest
        rows.sort(key=lambda r: (r["avg"] is not None, avg_key(r)), reverse=True)

    return questions, rows
