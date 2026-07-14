"""Packs, pack groups, applicant submissions and application review.

Applicants apply to a PackGroup: the form walks them through each pack in
the group, creating one Application row per pack that all share one
``application_id``. Review, approval and interviews then operate on the
submission as a whole.
"""

import uuid
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from ..forms import ApplicantForm, PackForm
from ..models import Application, ApplicationPack, Pack, PackGroup
from ..permissions import ASSESSOR_GROUP, ECAM_GROUP, ECD_GROUP, group_required


def submission_rows(application_id):
    """All Application rows of one submission (one per pack), oldest first.

    The first row is the submission's primary application: interview packs,
    results and indicator scores are stored against it.
    """
    return list(
        Application.objects
        .filter(application_id=application_id)
        .select_related("user", "group", "pack")
        .order_by("id")
    )


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def applications(request):
    """The pack groups an applicant can start an application for."""
    groups = PackGroup.objects.prefetch_related("packs").order_by("-id")

    return render(request, "pre_interview/applications.html", {
        "groups": groups,
        "applications": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def create_pack(request):
    form = PackForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pack created successfully.")
        return redirect("applications")

    return render(request, "pre_interview/create_pack.html", {
        "form": form,
        "create_pack": True,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def select_packs(request):
    """Create a pack group from a selection of packs."""
    packs = Pack.objects.order_by("-id")

    if request.method == "POST":
        selected_pack_ids = request.POST.getlist("packs")
        group_name = request.POST.get("group_name", "").strip()

        if not selected_pack_ids:
            messages.error(request, "Please select at least one pack.")
            return redirect("select_packs")

        if not group_name:
            messages.error(request, "Please give the pack group a name.")
            return redirect("select_packs")

        pack_group = PackGroup.objects.create(name=group_name)
        pack_group.packs.set(Pack.objects.filter(id__in=selected_pack_ids))

        messages.success(
            request,
            f"Pack group '{group_name}' created with {pack_group.packs.count()} packs.",
        )
        return redirect("group_list")

    return render(request, "pre_interview/select_packs.html", {
        "packs": packs,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def group_list(request):
    """Overview of the pack groups that have been created."""
    groups = PackGroup.objects.prefetch_related("packs").order_by("name")

    return render(request, "pre_interview/group_list.html", {
        "groups": groups,
    })


@login_required
def applicant_form_group(request, group_id, step=0):
    """Step an applicant through the pre-interview form of every pack in a group."""
    group = get_object_or_404(
        PackGroup.objects.prefetch_related("packs"),
        id=group_id,
    )
    packs = list(group.packs.all())

    if not packs:
        messages.error(request, "This group has no packs to apply to.")
        return redirect("applications")

    if step >= len(packs):
        request.session.pop("group_application_id", None)
        messages.success(request, "Application submitted successfully!")
        return redirect("applications")

    # A missing submission id (expired session, direct URL) restarts the flow.
    if step > 0 and not request.session.get("group_application_id"):
        return redirect("applicant_form_group", group_id=group_id, step=0)

    pack = packs[step]
    form = ApplicantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        if step == 0:
            request.session["group_application_id"] = str(uuid.uuid4())
        submission_id = request.session["group_application_id"]

        # update_or_create keeps back-button resubmits from duplicating rows.
        Application.objects.update_or_create(
            application_id=submission_id,
            pack=pack,
            defaults={
                "user": request.user,
                "group": group,
                "answer_1": form.cleaned_data["answer_1"],
                "answer_2": form.cleaned_data["answer_2"],
                "answer_3": form.cleaned_data["answer_3"],
            },
        )

        return redirect("applicant_form_group", group_id=group_id, step=step + 1)

    return render(request, "pre_interview/applicant_form.html", {
        "group": group,
        "pack": pack,
        "form": form,
        "step": step,
        "total": len(packs),
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_review(request):
    """Every submission, one row per shared application_id."""
    applications = (
        Application.objects
        .select_related("user", "pack", "group")
        .order_by("-created_at")
    )

    grouped = defaultdict(list)
    for application in applications:
        grouped[application.application_id].append(application)

    return render(request, "pre_interview/application_review.html", {
        "grouped_applications": list(grouped.values()),
        "applications": True,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_detail(request, application_id):
    """Every pack's questions and answers for one submission."""
    rows = submission_rows(application_id)
    if not rows:
        raise Http404("No application with this id.")

    return render(request, "pre_interview/view_more.html", {
        "application": rows[0],
        "group_applications": rows,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def approve_application(request, application_id):
    """Accept a submission: set the interview date and choose interview packs.

    The chosen packs become ApplicationPack rows on the submission's primary
    application; when none are chosen the interview defaults to the packs the
    applicant applied to.
    """
    rows = submission_rows(application_id)
    if not rows:
        raise Http404("No application with this id.")
    application = rows[0]

    if request.method == "POST":
        interview_date = parse_datetime(request.POST.get("interview_date") or "")
        if interview_date and timezone.is_naive(interview_date):
            interview_date = timezone.make_aware(interview_date)

        Application.objects.filter(application_id=application_id).update(
            status=Application.STATUS_ACCEPTED,
            interview_date=interview_date,
        )

        selected_ids = []
        for raw_id in request.POST.getlist("interview_packs"):
            try:
                selected_ids.append(int(raw_id))
            except (TypeError, ValueError):
                continue

        application.interview_packs.all().delete()
        packs_by_id = Pack.objects.in_bulk(selected_ids)
        for order, pack_id in enumerate(selected_ids):
            pack = packs_by_id.get(pack_id)
            if pack:
                ApplicationPack.objects.create(
                    application=application, pack=pack, order=order,
                )

        messages.success(
            request,
            f"Application for {application.user.username} approved successfully!",
        )
        return redirect("application_review")

    return render(request, "pre_interview/schedule_interview.html", {
        "application": application,
        "all_packs": Pack.objects.order_by("title"),
        "submission_pack_ids": [row.pack_id for row in rows],
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def deny_application(request, application_id):
    if request.method == "POST":
        updated = Application.objects.filter(
            application_id=application_id,
        ).update(status=Application.STATUS_DENIED)

        if updated:
            messages.error(request, "Application denied.")

    return redirect("application_review")


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def accepted_applicants(request):
    """Accepted submissions, ready for their interview to be started."""
    applications = (
        Application.objects
        .filter(status=Application.STATUS_ACCEPTED)
        .select_related("user", "group", "pack")
        .order_by("interview_date")
    )

    grouped = defaultdict(list)
    for application in applications:
        grouped[application.application_id].append(application)

    return render(request, "pre_interview/accepted_applicants.html", {
        "grouped_applicants": list(grouped.values()),
        "applications": True,
    })
