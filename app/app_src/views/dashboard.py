"""Results listing and the candidate performance dashboard."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from ..models import Application
from ..permissions import ECAM_GROUP, ECD_GROUP, group_required
from ..services.dashboard import candidate_dashboard_data
from ..services.pdf import render_candidate_dashboard_pdf


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def results_view(request):
    applications = (
        Application.objects
        .select_related("user")
        .prefetch_related("results__question")
        .order_by("-created_at")
    )

    return render(request, "results/results.html", {
        "page_title": settings.APPLICATION_NAME + " - Results",
        "applications": applications,
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
