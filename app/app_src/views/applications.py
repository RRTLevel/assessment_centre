"""Packs, applicant submissions and application review."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ApplicantForm, PackForm
from ..models import Application, Pack, PackGroup, Application
from ..models import Application, ApplicationPack, Pack
from ..permissions import ASSESSOR_GROUP, ECAM_GROUP, ECD_GROUP, group_required
from django.contrib.auth.models import Group

from collections import defaultdict



@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def applications(request):
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
        return redirect("applications")

    return render(request, "pre_interview/create_pack.html", {
        "form": form,
        "create_pack": True,
    })


import uuid

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def applicant_form(request, pack_id):
    pack = get_object_or_404(Pack, id=pack_id)
    form = ApplicantForm(request.POST or None)

    # 🔥 get group (assuming 1 group per pack)
    group = pack.groups.first()

    if request.method == "POST" and form.is_valid():

        # ✅ check if user already started this group submission
        existing_application = Application.objects.filter(
            user=request.user,
            pack__groups=group,
            status=Application.STATUS_PENDING
        ).first()

        if existing_application:
            submission_id = existing_application.application_id
        else:
            submission_id = uuid.uuid4()

        application = form.save(commit=False)
        application.user = request.user
        application.pack = pack
        application.group = group
        application.application_id = submission_id
        application.save()

        return redirect("applications")

    return render(request, "pre_interview/applicant_form.html", {
        "pack": pack,
        "form": form,
    })


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_review(request):

    applications = Application.objects.select_related(
        "user",
        "pack",
        "group"
    ).order_by("-created_at")


    grouped = defaultdict(list)

    for application in applications:
        grouped[application.application_id].append(application)


    return render(request, "pre_interview/application_review.html", {
        "grouped_applications": list(grouped.values()),
        "applications_active": True,
    })

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def application_detail(request, application_id):
    application = get_object_or_404(
        Application,
        application_id=application_id
    )

    return render(request, "pre_interview/view_more.html", {
        "application": application,
    })

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def approve_application(request, application_id):

    applications = Application.objects.filter(
        application_id=application_id
    )

    if request.method == "POST":

        interview_date = request.POST.get("interview_date")

        applications.update(
            status=Application.STATUS_ACCEPTED,
            interview_date=interview_date
        )

        messages.success(
            request,
            "Application group approved successfully!"
        )

        return redirect("application_review")

    return render(request, "pre_interview/schedule_interview.html", {
        "application": applications.first(),
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

    return render(request, "pre_interview/schedule_interview.html", {
        "application": application,
        "all_packs": Pack.objects.all().order_by("title"),
    })

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def deny_application(request, application_id):

    if request.method == "POST":

        Application.objects.filter(
            application_id=application_id
        ).update(
            status=Application.STATUS_DENIED
        )

        messages.error(
            request,
            "Application group denied."
        )

    return redirect("application_review")


@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def accepted_applicants(request):

    applications = Application.objects.filter(
        status=Application.STATUS_ACCEPTED
    ).select_related("user", "group", "pack")

    grouped = defaultdict(list)

    for app in applications:
        grouped[app.application_id].append(app)

    return render(request, "pre_interview/accepted_applicants.html", {
        "grouped_applicants": list(grouped.values()),
        "applications": True,
    })

@login_required
@group_required(ECD_GROUP, ECAM_GROUP)
def select_packs(request):
    packs = Pack.objects.order_by("-id")

    if request.method == "POST":
        selected_pack_ids = request.POST.getlist("packs")
        group_name = request.POST.get("group_name")

        if not selected_pack_ids:
            messages.error(request, "Please select at least one pack.")
            return redirect("select_packs")

        if not group_name:
            messages.error(request, "Please give the pack group a name.")
            return redirect("select_packs")

        selected_packs = Pack.objects.filter(
            id__in=selected_pack_ids
        )

        pack_group = PackGroup.objects.create(
            name=group_name
        )

        pack_group.packs.set(selected_packs)

        messages.success(
            request,
            f"Pack group '{group_name}' created successfully with {len(selected_pack_ids)} packs."
        )

        return redirect("applications")

    return render(request, "pre_interview/select_packs.html", {
        "packs": packs,
    })


@login_required
def group_list(request):
    groups = PackGroup.objects.prefetch_related("packs").order_by("name")

    return render(request, "pre_interview/group_list.html", {
        "groups": groups,
    })


@login_required
def applicant_form_group(request, group_id, step=0):

    group = get_object_or_404(
        PackGroup.objects.prefetch_related("packs"),
        id=group_id
    )

    packs = list(group.packs.all())

    if step >= len(packs):
        # finished application
        request.session.pop("application_id", None)
        return redirect("applications")

    pack = packs[step]


    if request.method == "POST":

        form = ApplicantForm(request.POST)

        if form.is_valid():

            # Create a NEW submission ID only at the start
            if step == 0:
                submission_id = uuid.uuid4()
                request.session["application_id"] = str(submission_id)

            else:
                submission_id = request.session.get("application_id")


            application = form.save(commit=False)

            application.user = request.user
            application.group = group
            application.pack = pack
            application.application_id = submission_id

            application.save()


            return redirect(
                "applicant_form_group",
                group_id=group_id,
                step=step + 1
            )


    else:
        form = ApplicantForm()


    return render(request, "pre_interview/applicant_form.html", {
        "group": group,
        "pack": pack,
        "form": form,
        "step": step,
        "total": len(packs),
    })