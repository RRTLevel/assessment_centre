"""Results listing and the candidate performance dashboard."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.dashboard import candidate_dashboard_data, interview_results_by_candidate
from ..services.pdf import render_candidate_dashboard_pdf


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def results_view(request):
    """Interview results per candidate submission, organised by pack: the
    scores, notes and feedback recorded per question plus the indicator
    assessment."""
    candidates = interview_results_by_candidate()

    return render(request, "results/results.html", {
        "page_title": settings.APPLICATION_NAME + " - Results",
        "candidates": candidates,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def candidate_dashboard(request):
    """Heatmap of question scores, one row per interviewed submission."""
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
    """PDF export of the dashboard heatmap plus per-candidate detail pages."""
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
