"""Results listing and the candidate performance dashboard."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Prefetch, Q
from django.http import HttpResponse
from django.shortcuts import render

from ..models import Genre, InterviewResult, Questions

from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.dashboard import candidate_dashboard_data
from ..services.pdf import render_candidate_dashboard_pdf


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def results_view(request):
    """Every interview question with the scored responses recorded against it."""
    questions = list(
        Questions.objects
        .select_related("category")
        .order_by("id")
        .annotate(avg_score=Avg("interviewresult__score"))
        .prefetch_related(
            Prefetch(
                "interviewresult_set",
                queryset=(
                    InterviewResult.objects
                    .select_related("application__user")
                    .order_by("-updated_at")
                ),
                to_attr="responses",
            )
        )
    )

    genre_summary = []
    for genre in Genre.objects.select_related("pack_1", "pack_2", "pack_3").order_by("name"):
        pack_list = genre.packs()
        cat_ids = [p.category_id for p in pack_list if p.category_id]
        if cat_ids:
            qs = InterviewResult.objects.filter(question__category_id__in=cat_ids)
            avg = qs.aggregate(avg=Avg("score"))["avg"]
            count = qs.count()
        else:
            avg, count = None, 0
        genre_summary.append({
            "genre": genre,
            "packs": pack_list,
            "avg_score": round(avg, 1) if avg is not None else None,
            "response_count": count,
        })

    return render(request, "results/results.html", {
        "page_title": settings.APPLICATION_NAME + " - Results",
        "questions_with_responses": [(question, question.responses, question.avg_score) for question in questions],
        "total_responses": sum(len(question.responses) for question in questions),
        "genre_summary": genre_summary,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def candidate_dashboard(request):
    questions, rows = candidate_dashboard_data(
        date_from=request.GET.get("from"),
        date_to=request.GET.get("to"),
        sort=request.GET.get("sort"),
    )

    return render(request, "statistics_dashboard/candidate_dashboard.html", {
        "questions": questions,
        "rows": rows,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def candidate_dashboard_pdf(request):
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    questions, rows = candidate_dashboard_data(
        date_from=date_from,
        date_to=date_to,
        sort=request.GET.get("sort"),
    )

    pdf = render_candidate_dashboard_pdf(questions, rows, date_from, date_to)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="candidate_performance.pdf"'
    return response
