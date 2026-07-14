"""Loading and saving the multi-pack interview for one submission.

A submission is the set of Application rows sharing one ``application_id``
(one row per pack of the group the applicant applied to). Interview results
and indicator scores are stored against the submission's primary row — the
first Application — via the ApplicationPack rows hanging off it.
"""

import re

from ..models import (
    ApplicationPack,
    Indicator,
    IndicatorGroupScore,
    IndicatorScore,
    InterviewResult,
    Question,
)

INDICATOR_SCORE_KEY = re.compile(r"^indicator_score_(\d+)$")
GROUP_SCORE_PREFIX = "group_score_"
GROUP_NOTES_PREFIX = "group_notes_"


def get_interview_packs(application, submission_rows=None):
    """The packs chosen for this interview, in order.

    When none were chosen at scheduling, defaults to one ApplicationPack per
    pack of the submission (every row of a group application).
    """
    packs = list(
        application.interview_packs.select_related("pack__category").order_by("order")
    )
    if packs:
        return packs

    for order, row in enumerate(submission_rows or [application]):
        ApplicationPack.objects.get_or_create(
            application=application,
            pack=row.pack,
            defaults={"order": order},
        )

    return list(
        application.interview_packs.select_related("pack__category").order_by("order")
    )


def interview_context(application, interview_packs):
    """Everything the interview page needs: per-pack question data plus the
    indicator groups and previously saved scores for the page script."""
    saved = {result.question_id: result for result in application.results.all()}

    pack_data = []
    total_questions = 0
    for ap in interview_packs:
        questions = list(Question.objects.filter(category=ap.pack.category))
        total_questions += len(questions)
        pack_data.append({
            "ap": ap,
            "pack": ap.pack,
            "question_data": [
                {"question": question, "result": saved.get(question.id)}
                for question in questions
            ],
        })

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
        "pack_data": pack_data,
        "total_questions": total_questions,
        "indicator_groups": indicator_groups,
        "saved_indicator_scores": saved_indicator_scores,
        "saved_group_scores": saved_group_scores,
        "saved_group_notes": saved_group_notes,
    }


def save_interview_submission(application, interview_packs, post_data):
    """Persist the per-question results and indicator scores, then refresh the
    submission's average score.

    Form field names match the interview page: ``notes_<ap>_<q>``,
    ``feedback_<ap>_<q>``, ``overall_score_<ap>_<q>``, ``indicator_score_<id>``,
    ``group_score_<name>`` and ``group_notes_<name>``.
    """
    overall_scores = []

    for ap in interview_packs:
        for question in Question.objects.filter(category=ap.pack.category):
            notes = post_data.get(f"notes_{ap.id}_{question.id}", "")
            feedback = post_data.get(f"feedback_{ap.id}_{question.id}", "")
            score = _parse_score(post_data.get(f"overall_score_{ap.id}_{question.id}"))

            if score is not None:
                overall_scores.append(score)

            InterviewResult.objects.update_or_create(
                application=application,
                question=question,
                defaults={
                    "score": score,
                    "notes": notes,
                    "feedback": feedback,
                    "application_pack": ap,
                },
            )

    _save_indicator_scores(application, post_data)

    application.average_score = (
        round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else None
    )
    application.save(update_fields=["average_score"])


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
