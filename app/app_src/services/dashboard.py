"""Query logic behind the candidate performance dashboard and its PDF export."""

from django.contrib.auth.models import User
from django.db.models import Avg, Prefetch

from ..models import Application, InterviewResult, Questions

SORT_OPTIONS = {
    "highest": "-avg",
    "lowest": "avg",
    "newest": "-application__created_at",
    "oldest": "application__created_at",
}

DEFAULT_SORT = "-avg"


def candidate_dashboard_data(date_from=None, date_to=None, sort=None):
    """Build the dashboard heatmap: one row per interviewed candidate.

    Returns ``(questions, rows)`` where each row has the candidate's name,
    latest application, per-question scores (aligned with ``questions``)
    and their average score.
    """
    questions = list(Questions.objects.order_by("id"))

    users = (
        User.objects
        .filter(application__results__isnull=False)
        .distinct()
        .annotate(avg=Avg("application__results__score"))
    )

    if date_from:
        users = users.filter(application__created_at__date__gte=date_from)

    if date_to:
        users = users.filter(application__created_at__date__lte=date_to)

    users = users.order_by(SORT_OPTIONS.get(sort, DEFAULT_SORT))

    # Latest application per user, with its results, in a single query each
    # (instead of two queries per candidate).
    applications = (
        Application.objects
        .filter(user__in=users)
        .select_related("pack")
        .prefetch_related(
            Prefetch(
                "results",
                queryset=InterviewResult.objects.select_related("question").order_by("question_id"),
            )
        )
        .order_by("user_id", "-created_at")
    )

    latest_application = {}
    for application in applications:
        latest_application.setdefault(application.user_id, application)

    rows = []

    for user in users:
        application = latest_application.get(user.id)

        scores = {}
        if application:
            scores = {result.question_id: result.score for result in application.results.all()}

        rows.append({
            "name": user.username,
            "date": application.created_at if application else None,
            "cells": [scores.get(question.id) for question in questions],
            "avg": user.avg,
            "application": application,
        })

    return questions, rows
