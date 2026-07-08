"""Saving and loading interview scoring for an application."""

import json
import re

from ..models import Indicator, IndicatorGroupScore, IndicatorScore, InterviewResult

INDICATOR_SCORE_KEY = re.compile(r"^indicator_score_(\d+)$")
GROUP_SCORE_PREFIX = "group_score_"
GROUP_NOTES_PREFIX = "group_notes_"


def interview_context(application, questions):
    """Everything the interview page needs: per-question results plus the
    indicator groups and previously saved scores as JSON for the page script."""
    saved = {result.question_id: result for result in application.results.all()}
    question_data = [
        {"question": question, "result": saved.get(question.id)}
        for question in questions
    ]

    saved_indicator_scores = {
        score.indicator_id: score.score
        for score in application.indicator_scores.all()
    }

    saved_group_scores = {}
    saved_group_notes = {}
    for group in application.indicator_group_scores.all():
        saved_group_scores[group.group_name] = group.score
        saved_group_notes[group.group_name] = group.notes

    indicator_groups = {}
    for indicator in Indicator.objects.order_by("name", "id"):
        indicator_groups.setdefault(indicator.name, []).append({
            "id": indicator.id,
            "positive": indicator.positive,
            "negative": indicator.negative,
        })

    return {
        "question_data": question_data,
        "indicator_groups_json": json.dumps(indicator_groups),
        "saved_indicator_scores_json": json.dumps(saved_indicator_scores),
        "saved_group_scores_json": json.dumps(saved_group_scores),
        "saved_group_notes_json": json.dumps(saved_group_notes),
    }


def save_interview_submission(application, questions, post_data):
    """Persist the per-question results, per-indicator and per-group scores,
    then store the candidate's average score on the application."""
    overall_scores = []

    for question in questions:
        notes = post_data.get(f"notes_{question.id}", "")
        feedback = post_data.get(f"feedback_{question.id}", "")
        overall_score = _parse_score(post_data.get(f"overall_score_{question.id}"))

        if overall_score is not None:
            overall_scores.append(overall_score)

        InterviewResult.objects.update_or_create(
            application=application,
            question=question,
            defaults={"score": overall_score, "notes": notes, "feedback": feedback},
        )

    _save_indicator_scores(application, post_data)

    application.average_score = (
        round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else None
    )
    application.save()


def _save_indicator_scores(application, post_data):
    for key, value in post_data.items():
        score = _parse_score(value)

        match = INDICATOR_SCORE_KEY.match(key)
        if match and score is not None:
            indicator = Indicator.objects.filter(id=int(match.group(1))).first()
            if indicator:
                IndicatorScore.objects.update_or_create(
                    application=application,
                    indicator=indicator,
                    defaults={"score": score},
                )

        if key.startswith(GROUP_SCORE_PREFIX) and score is not None:
            group_name = key[len(GROUP_SCORE_PREFIX):]
            if group_name:
                IndicatorGroupScore.objects.update_or_create(
                    application=application,
                    group_name=group_name,
                    defaults={
                        "score": score,
                        "notes": post_data.get(f"{GROUP_NOTES_PREFIX}{group_name}", ""),
                    },
                )


def _parse_score(raw):
    return int(raw) if raw and raw.isdigit() else None
