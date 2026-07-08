"""Saving and loading interview scoring for an application."""

from ..models import IndicatorScore, InterviewResult


def interview_questions_with_results(application, questions):
    """Pair each question with any previously saved result and indicator scores."""
    saved = {
        result.question_id: result
        for result in application.results.prefetch_related("indicator_scores").all()
    }

    question_data = []
    for question in questions:
        result = saved.get(question.id)

        saved_scores = {}
        if result:
            saved_scores = {score.indicator_id: score.score for score in result.indicator_scores.all()}

        question_data.append({
            "question": question,
            "result": result,
            "indicators": list(question.indicators.all()),
            "saved_scores": saved_scores,
        })

    return question_data


def save_interview_submission(application, questions, post_data):
    """Persist the scores, notes and feedback submitted for each question,
    then store the candidate's average score on the application."""
    overall_scores = []

    for question in questions:
        notes = post_data.get(f"notes_{question.id}", "")
        feedback = post_data.get(f"feedback_{question.id}", "")
        overall_score = _parse_score(post_data.get(f"overall_score_{question.id}"))

        if overall_score is not None:
            overall_scores.append(overall_score)

        result, _created = InterviewResult.objects.update_or_create(
            application=application,
            question=question,
            defaults={"score": overall_score, "notes": notes, "feedback": feedback},
        )

        for indicator in question.indicators.all():
            score = _parse_score(post_data.get(f"indicator_score_{question.id}_{indicator.id}"))
            if score is not None:
                IndicatorScore.objects.update_or_create(
                    result=result,
                    indicator=indicator,
                    defaults={"score": score},
                )

    application.average_score = (
        round(sum(overall_scores) / len(overall_scores), 2) if overall_scores else None
    )
    application.save()


def _parse_score(raw):
    return int(raw) if raw and raw.isdigit() else None
