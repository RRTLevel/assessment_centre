"""Query logic behind the candidate performance dashboard and its PDF export."""

from collections import defaultdict

from django.db.models import Prefetch

from ..models import Application, InterviewResult, Question


def candidate_dashboard_data(date_from=None, date_to=None, sort=None):
    """
    Build the dashboard heatmap: one row per interviewed candidate (group-based).

    Each row represents:
        - One user
        - One group (collection of packs)
        - Combined results across ALL packs in that group
    """

    # 🔹 All questions (columns)
    questions = list(Question.objects.order_by("id"))

    # 🔹 Get ALL applications that have interview results
    applications = (
        Application.objects
        .filter(results__isnull=False)
        .select_related("user", "group", "pack")
        .prefetch_related(
            Prefetch(
                "results",
                queryset=InterviewResult.objects.select_related("question").order_by("question_id"),
            )
        )
    )

    # 🔹 Optional date filters
    if date_from:
        applications = applications.filter(created_at__date__gte=date_from)

    if date_to:
        applications = applications.filter(created_at__date__lte=date_to)

    # 🔹 GROUP applications by (user, group)
    grouped = defaultdict(list)

    for app in applications:
        key = (app.user_id, app.group_id)
        grouped[key].append(app)

    rows = []

    # 🔹 Build dashboard rows
    for (user_id, group_id), apps in grouped.items():
        user = apps[0].user
        group = apps[0].group

        # Collect scores across ALL packs
        scores = {}
        all_scores = []

        for app in apps:
            for result in app.results.all():
                if result.score is not None:
                    scores[result.question_id] = result.score
                    all_scores.append(result.score)

        # Calculate average score across packs
        avg = round(sum(all_scores) / len(all_scores), 2) if all_scores else None

        rows.append({
            "name": user.username,
            "group": group.name,
            "date": max(app.created_at for app in apps),
            "cells": [scores.get(question.id) for question in questions],
            "avg": avg,
            "applications": apps,  # useful for drill-down later
        })

    # 🔹 Sorting
    if sort == "lowest":
        rows.sort(key=lambda r: (r["avg"] is None, r["avg"]))
    elif sort == "newest":
        rows.sort(key=lambda r: r["date"], reverse=True)
    elif sort == "oldest":
        rows.sort(key=lambda r: r["date"])
    else:  # default = highest
        rows.sort(key=lambda r: (r["avg"] is None, r["avg"]), reverse=True)

    return questions, rows