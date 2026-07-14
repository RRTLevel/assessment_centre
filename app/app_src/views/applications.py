"""Packs, applicant submissions and application review."""

import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ApplicantForm, PackForm
from ..models import Application, ApplicationPack, Genre, Pack
from ..permissions import ASSESSOR_GROUP, ECAM_GROUP, ECD_GROUP, group_required


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def applications(request):
    packs = Pack.objects.order_by("-created_at")
    return render(request, "pre_interview/applications.html", {
        "packs": packs,
        "applications": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def create_pack(request):
    form = PackForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("applications")

    return render(request, "pre_interview/create_pack.html", {
        "form": form,
        "create_pack": True,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def applicant_form(request, pack_id):
    pack = get_object_or_404(Pack, id=pack_id)
    form = ApplicantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.user = request.user
        application.pack = pack
        application.save()
        return redirect("applications")

    return render(request, "pre_interview/applicant_form.html", {
        "pack": pack,
        "form": form,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_review(request):
    applications_list = Application.objects.select_related("user", "pack")
    return render(request, "pre_interview/application_review.html", {
        "applications": applications_list,
        "applications_active": True,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_detail(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)
    return render(request, "pre_interview/view_more.html", {
        "application": application,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def approve_application(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)

    if request.method == "POST":
        interview_date = request.POST.get("interview_date")
        application.status = Application.STATUS_ACCEPTED
        if interview_date:
            application.interview_date = interview_date
        application.save()

        selected_ids = request.POST.getlist("interview_packs")
        application.interview_packs.all().delete()
        for order, pack_id in enumerate(selected_ids):
            try:
                pack = Pack.objects.get(id=int(pack_id))
                ApplicationPack.objects.create(application=application, pack=pack, order=order)
            except (Pack.DoesNotExist, ValueError):
                pass

        messages.success(request, f"Application for {application.user.username} approved successfully!")
        return redirect("application_review")

    genres = Genre.objects.select_related("pack_1", "pack_2", "pack_3").order_by("name")
    genres_data = [
        {
            "id": g.id,
            "name": g.name,
            "pack_ids": [p.id for p in g.packs()],
        }
        for g in genres
    ]
    return render(request, "pre_interview/schedule_interview.html", {
        "application": application,
        "all_packs": Pack.objects.all().order_by("title"),
        "genres": genres,
        "genres_json": json.dumps(genres_data),
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def deny_application(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)

    if request.method == "POST":
        application.status = Application.STATUS_DENIED
        application.save()
        messages.error(request, f"Application for {application.user.username} was denied.")

    return redirect("application_review")


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def accepted_applicants(request):
    applicants = Application.objects.filter(status=Application.STATUS_ACCEPTED)
    return render(request, "pre_interview/accepted_applicants.html", {
        "applicants": applicants,
        "applications": True,
    })
