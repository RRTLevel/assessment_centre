"""Results listing and the candidate performance dashboard."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render

from ..models import InterviewResult, Question
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.dashboard import candidate_dashboard_data
from ..services.pdf import render_candidate_dashboard_pdf


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def results_view(request):
    """Every interview question with the scored responses recorded against it."""

    questions = list(
        Question.objects
        .select_related("category")
        .order_by("id")
        .prefetch_related(
            Prefetch(
                "interviewresult_set",
                queryset=(
                    InterviewResult.objects
                    .select_related("application__user", "application__group", "application__pack")
                    .order_by("-updated_at")
                ),
                to_attr="responses",
            )
        )
    )

    return render(request, "results/results.html", {
        "page_title": settings.APPLICATION_NAME + " - Results",
        "questions_with_responses": [(q, q.responses) for q in questions],
        "total_responses": sum(len(q.responses) for q in questions),
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def candidate_dashboard(request):
    """Main grouped dashboard (user + group)."""

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
    """PDF export of grouped dashboard."""

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