import calendar
import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.models import User


from .forms import (
    AddNoteForm,
    ApplicantForm,
    CategoryForm,
    DomainUserCreationForm,
    IndicatorForm,
    InterviewResponseForm,
    PackForm,
    QuestionForm,
)
from .models import (
    Application,
    Category,
    Indicator,
    InterviewResult,
    Note,
    Pack,
    Questions,
)
from .permissions import ASSESSOR_GROUP, ECAM_GROUP, ECD_GROUP, group_required


class RememberMeLoginView(LoginView):
    template_name = "registration/login.html"
    REMEMBER_ME_AGE = 60 * 60 * 24 * 30

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

    def form_valid(self, form):
        if self.request.POST.get("remember_me"):
            self.request.session.set_expiry(self.REMEMBER_ME_AGE)
        else:
            self.request.session.set_expiry(0)

        return super().form_valid(form)


class DeleteAccountView(LoginRequiredMixin, View):
    login_url = "/login"

    def post(self, request):
        password = request.POST.get("password")

        if not request.user.check_password(password):
            messages.error(request, "Incorrect password.")
            return redirect("userprofile")

        user = request.user
        logout(request)
        user.delete()
        return redirect("/")


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = DomainUserCreationForm
    success_url = reverse_lazy("login")
    success_message = "Your account has been created!"
    template_name = "registration/signup.html"


class userprofileView(LoginRequiredMixin, TemplateView):
    login_url = "/login"
    template_name = "notes/userprofile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = settings.APPLICATION_NAME + " - Profile"
        context["AccountType"] = self.request.user.groups.first()
        return context

    def post(self, request, **kwargs):
        user = request.user
        old_pass = request.POST.get("old_password")
        new_pass1 = request.POST.get("new_password1")
        new_pass2 = request.POST.get("new_password2")

        if not user.check_password(old_pass):
            messages.error(request, "Incorrect current password.")
            return redirect("userprofile")

        if new_pass1 != new_pass2:
            messages.error(request, "Passwords do not match.")
            return redirect("userprofile")

        if len(new_pass1) < 8:
            messages.error(request, "Password too short.")
            return redirect("userprofile")

        user.set_password(new_pass1)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated.")
        return redirect("userprofile")


class homeView(LoginRequiredMixin, CreateView):
    login_url = "/login"
    form_class = AddNoteForm
    model = Note
    template_name = "notes/notes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = True
        context["notes"] = Note.objects.order_by("-pub_date")[:5]
        context["page_title"] = settings.APPLICATION_NAME + " - Notes"
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("home")


def documentationView(request):
    return render(request, "notes/documentation.html")


def helpView(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def add_indicators(request):
    if request.method == "POST":
        form = IndicatorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_indicators")
    else:
        form = IndicatorForm()

    questions = Questions.objects.prefetch_related("indicators").all()
    return render(request, "indicators/add_indicators.html", {
        "page_title": settings.APPLICATION_NAME + " - Add Indicators",
        "form": form,
        "questions": questions,
    })

@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def resultsView(request):
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

@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def applications(request):
    packs = Pack.objects.all().order_by("-created_at")
    return render(request, "pre_interview/applications.html", {
        "packs": packs,
        "applications": True,
    })


@login_required(login_url="/login")
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





@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def applicant_form(request, pack_id):
    pack = get_object_or_404(Pack, id=pack_id)
    form = ApplicantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        Application.objects.create(
            user=request.user,
            pack=pack,
            answer_1=form.cleaned_data["answer_1"],
            answer_2=form.cleaned_data["answer_2"],
            answer_3=form.cleaned_data["answer_3"],
        )
        return redirect("applications")

    return render(request, "pre_interview/applicant_form.html", {
        "pack": pack,
        "form": form,
    })


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def add_question(request):
    form = QuestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.cleaned_data["category"]
        for i in range(1, 6):
            text = form.cleaned_data[f"question_{i}"]
            if text and text.strip():
                Questions.objects.create(text=text, category=category)

        return redirect("add_questions")

    questions = Questions.objects.select_related("category").all().order_by("-id")
    return render(request, "add_questions/add_questions.html", {
        "form": form,
        "questions": questions,
        "add_question": True,
    })


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def question_list(request):
    questions = Questions.objects.select_related("category").order_by("-id")
    return render(request, "add_questions/question_list.html", {
        "questions": questions,
        "add_question": True,
    })


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def delete_question(request, pk):
    question = get_object_or_404(Questions, pk=pk)
    if request.method == "POST":
        question.delete()
    return redirect("question_list")


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def create_category(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("categories")

    return render(request, "pre_interview/create_category.html", {
        "form": form,
        "categories": Category.objects.all(),
    })


@login_required(login_url="/login")
@group_required(ASSESSOR_GROUP)
def delete_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == "POST":
        category.delete()
    return redirect("categories")


@login_required(login_url="/login")
def load_questions(request):
    category_id = request.GET.get("category")

    if not category_id:
        return JsonResponse([], safe=False)

    questions = Questions.objects.filter(category_id=category_id).values("id", "text")
    return JsonResponse(list(questions), safe=False)


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def application_review(request):
    applications_list = Application.objects.select_related("user", "pack")
    return render(request, "pre_interview/application_review.html", {
        "applications": applications_list,
        "applications_active": True,
    })


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def application_detail(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)
    return render(request, "pre_interview/view_more.html", {
        "application": application,
    })


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def approve_application(request, pk=None, application_id=None):
    lookup_id = application_id or pk
    application = get_object_or_404(Application, application_id=lookup_id)

    if request.method == "POST":
        interview_date = request.POST.get("interview_date")
        application.status = "Accepted"
        if interview_date:
            application.interview_date = interview_date
        application.save()
        messages.success(request, f"Application for {application.user.username} approved successfully!")
        return redirect("application_review")

    return render(request, "pre_interview/schedule_interview.html", {
        "application": application,
    })


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def deny_application(request, pk=None, application_id=None):
    lookup_id = application_id or pk
    application = get_object_or_404(Application, application_id=lookup_id)

    if request.method == "POST":
        application.status = "Denied"
        application.save()
        messages.error(request, f"Application for {application.user.username} was denied.")

    return redirect("application_review")


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def accepted_applicants(request):
    applicants = Application.objects.filter(status="Accepted")
    return render(request, "pre_interview/accepted_applicants.html", {
        "applicants": applicants,
        "applications": True,
    })


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def start_interview(request, application_id):
    application = get_object_or_404(Application, application_id=application_id)
    questions = Questions.objects.filter(category=application.pack.category)

    if request.method == "POST":
        scores = []

        for question in questions:
            score_raw = request.POST.get(f"score_{question.id}")
            notes = request.POST.get(f"notes_{question.id}", "")
            feedback = request.POST.get(f"feedback_{question.id}", "")
            score = int(score_raw) if score_raw and score_raw.isdigit() else None

            if score is not None:
                scores.append(score)

            InterviewResult.objects.update_or_create(
                application=application,
                question=question,
                defaults={
                    "score": score,
                    "notes": notes,
                    "feedback": feedback,
                },
            )

        application.average_score = round(sum(scores) / len(scores), 2) if scores else None
        application.save()
        messages.success(request, f"Interview for {application.user.username} submitted.")
        return redirect("inbox")

    saved = {result.question_id: result for result in application.results.all()}
    question_results = [(question, saved.get(question.id)) for question in questions]

    return render(request, "pre_interview/start_interview.html", {
        "application": application,
        "questions": questions,
        "question_results": question_results,
    })


@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def inbox_view(request):
    today = datetime.date.today()
    year_param = request.GET.get("year")
    month_param = request.GET.get("month")

    year = int(year_param) if year_param and year_param.isdigit() else today.year
    month = int(month_param) if month_param and month_param.isdigit() else today.month

    if month < 1 or month > 12:
        month = today.month

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    now = timezone.now()

    upcoming_interviews = (
        Application.objects.filter(interview_date__gte=now)
        .select_related("user", "pack")
        .prefetch_related("results__question")
        .order_by("interview_date")
    )

    past_interviews = (
        Application.objects.filter(interview_date__lt=now)
        .annotate(avg_score=Avg("results__score"))
        .select_related("user", "pack")
        .prefetch_related("results__question")
        .order_by("-interview_date")
    )

    month_interviews = Application.objects.filter(
        interview_date__year=year,
        interview_date__month=month,
    )
    marked_days = {
        application.interview_date.day
        for application in month_interviews
        if application.interview_date
    }

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    return render(request, "pre_interview/inbox.html", {
        "month_days": month_days,
        "month_name": calendar.month_name[month],
        "year": year,
        "today_day": today.day if today.month == month else None,
        "marked_days": marked_days,
        "upcoming_interviews": upcoming_interviews,
        "past_interviews": past_interviews,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
        "applications": True,
    })





@login_required(login_url="/login")
@group_required(ECD_GROUP, ECAM_GROUP)
def candidate_dashboard(request):
    questions = Questions.objects.all().order_by("id")

    users = (
        User.objects
        .filter(application__results__isnull=False)
        .distinct()
        .annotate(avg=Avg("application__results__score"))
    )

    # Filters
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")
    sort = request.GET.get("sort")

    if date_from:
        users = users.filter(application__created_at__date__gte=date_from)

    if date_to:
        users = users.filter(application__created_at__date__lte=date_to)

    if sort == "highest":
        users = users.order_by("-avg")
    elif sort == "lowest":
        users = users.order_by("avg")
    elif sort == "newest":
        users = users.order_by("-application__created_at")
    elif sort == "oldest":
        users = users.order_by("application__created_at")
    else:
        users = users.order_by("-avg")

    rows = []

    for user in users:
        application = (
            Application.objects
            .filter(user=user)
            .order_by("-created_at")
            .first()
        )

        results = InterviewResult.objects.filter(application=application)

        scores = {r.question_id: r.score for r in results}
        cells = [scores.get(q.id) for q in questions]

        rows.append({
            "name": user.username,
            "date": application.created_at if application else None,
            "cells": cells,
            "avg": user.avg,
        })

    context = {
        "questions": questions,
        "rows": rows,
    }

    return render(
        request,
        "statistics_dashboard/candidate_dashboard.html",
        context,
    )