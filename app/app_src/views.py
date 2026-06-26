import logging
import datetime
import calendar

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.contrib.auth.views import LoginView

from .forms import (
    AddNoteForm,
    DomainUserCreationForm,
    PackForm,
    ApplicantForm,
    CategoryForm,
    InterviewResponseForm,
    QuestionForm
)

from .models import (
    Note,
    Pack,
    Application,
    InterviewResponse,
    Questions,
    Category
)

logger = logging.getLogger("")


# =========================
# AUTH
# =========================

class RememberMeLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
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


# =========================
# USER PROFILE
# =========================

class userprofileView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'notes/userprofile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = settings.APPLICATION_NAME + ' - Profile'
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
# =========================
# HOME
# =========================

class homeView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    form_class = AddNoteForm
    model = Note
    template_name = 'notes/notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notes"] = Note.objects.order_by('-pub_date')[:5]
        context["page_title"] = settings.APPLICATION_NAME + ' - Notes'
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('home')


# =========================
# STATIC PAGES
# =========================

def documentationView(request):
    return render(request, "notes/documentation.html")


def helpView(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"


# =========================
# APPLICATIONS
# =========================

@login_required(login_url='/login')
def applications(request):
    packs = Pack.objects.all()
    return render(request, "pre_interview/applications.html", {"packs": packs})


@login_required(login_url='/login')
def create_pack(request):
    form = PackForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('applications')

    return render(request, "pre_interview/create_pack.html", {"form": form})


# =========================
# APPLICATION REVIEW
# =========================

@login_required(login_url='/login')
def application_review(request):
    apps = Application.objects.select_related('user', 'pack')
    return render(request, "pre_interview/application_review.html", {
        "applications": apps
    })


@login_required(login_url='/login')
def application_detail(request, application_id):
    app = get_object_or_404(Application, application_id=application_id)
    return render(request, "pre_interview/view_more.html", {"application": app})


# =========================
# APPROVE / DENY
# =========================

@login_required(login_url='/login')
def approve_application(request, application_id):
    app = get_object_or_404(Application, application_id=application_id)

    if request.method == "GET":
        return render(request, "pre_interview/schedule_interview.html", {
            "application": app
        })

    if request.method == "POST":
        app.status = "Accepted"

        interview_date = request.POST.get("interview_date")
        if interview_date:
            app.interview_date = interview_date

        app.save()
        messages.success(request, "Interview scheduled.")
        return redirect("application_review")


@login_required(login_url='/login')
def deny_application(request, application_id):
    app = get_object_or_404(Application, application_id=application_id)

    if request.method == "POST":
        app.status = "Denied"
        app.save()

    return redirect('application_review')


@login_required(login_url='/login')
def accepted_applicants(request):
    applicants = Application.objects.filter(status="Accepted")
    return render(request, "pre_interview/accepted_applicants.html", {
        "applicants": applicants
    })


@login_required(login_url='/login')
def start_interview(request, pk):
    application = get_object_or_404(Application, application_id=pk)
    questions = Questions.objects.filter(category=application.pack.category)
    return render(request, "pre_interview/start_interview.html", {
        "application": application,
        "questions": questions
    })
# =========================
# QUESTION LIST & CATEGORIES
# =========================

@login_required(login_url='/login')
def question_list(request):
    questions = Questions.objects.select_related('category').order_by('-id')
    return render(request, "add_questions/question_list.html", {
        "questions": questions
    })


@login_required(login_url='/login')
def add_question(request):
    form = QuestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.cleaned_data["category"]

        for i in range(1, 6):
            text = form.cleaned_data[f"question_{i}"]
            if text:
                Questions.objects.create(text=text, category=category)

        return redirect("add_questions")

    questions = Questions.objects.all()
    return render(request, "add_questions/add_questions.html", {
        "form": form,
        "questions": questions
    })


@login_required(login_url='/login')
def delete_question(request, pk):
    q = get_object_or_404(Questions, id=pk)
    if request.method == "POST":
        q.delete()
    return redirect("add_questions")


@login_required(login_url='/login')
def create_category(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("categories")

    return render(request, "pre_interview/create_category.html", {
        "form": form,
        "categories": Category.objects.all()
    })


@login_required(login_url='/login')
def delete_category(request, pk):
    c = get_object_or_404(Category, id=pk)
    if request.method == "POST":
        c.delete()
    return redirect("categories")


@login_required(login_url='/login')
def load_questions(request):
    category_id = request.GET.get("category")

    if not category_id:
        return JsonResponse([], safe=False)

    questions = Questions.objects.filter(category_id=category_id).values("id", "text")
    return JsonResponse(list(questions), safe=False)


# =========================
# INTERVIEW SYSTEM
# =========================

@login_required(login_url='/login')
def interview(request):
    questions = Questions.objects.all()

    saved = {
        r.question_id: r
        for r in InterviewResponse.objects.filter(user=request.user, question__in=questions)
    }

    question_forms = [
        (q, InterviewResponseForm(instance=saved.get(q.id), prefix=str(q.id)))
        for q in questions
    ]

    return render(request, "interview/interview.html", {
        "questions": questions,
        "question_forms": question_forms
    })


@login_required(login_url='/login')
def interview_save(request):
    if request.method == "POST":
        questions = Questions.objects.all()

        for q in questions:
            existing = InterviewResponse.objects.filter(
                user=request.user,
                question=q
            ).first()

            form = InterviewResponseForm(
                request.POST,
                instance=existing,
                prefix=str(q.id)
            )

            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user
                obj.question = q
                obj.save()

    return redirect("interview")


# =========================
# INBOX (FIXED DATETIME SAFE)
# =========================

@login_required(login_url='/login')
def inbox_view(request):
    today = datetime.date.today()

    year_param = request.GET.get("year")
    month_param = request.GET.get("month")

    year = int(year_param) if year_param and year_param.isdigit() else today.year
    month = int(month_param) if month_param and month_param.isdigit() else today.month

    if month < 1 or month > 12:
        month = today.month

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    all_interviews = Application.objects.filter(
        interview_date__isnull=False
    ).select_related('user', 'pack').order_by('interview_date')

    month_interviews = Application.objects.filter(
        interview_date__year=year,
        interview_date__month=month
    )

    marked_days = {
        a.interview_date.day
        for a in month_interviews
        if a.interview_date
    }

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)

    return render(request, "pre_interview/inbox.html", {
        "month_days": month_days,
        "month_name": calendar.month_name[month],
        "year": year,
        "today_day": today.day if today.month == month else None,
        "marked_days": marked_days,
        "interviews": all_interviews,
        "prev_month": prev_month,
        "prev_year": prev_year,
        "next_month": next_month,
        "next_year": next_year,
    })


# =========================
# APPLICATION FORM
# =========================

@login_required(login_url='/login')
def applicant_form(request, pack_id):
    pack = get_object_or_404(Pack, id=pack_id)
    form = ApplicantForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        a = form.cleaned_data

        Application.objects.create(
            user=request.user,
            pack=pack,
            answer_1=a["answer_1"],
            answer_2=a["answer_2"],
            answer_3=a["answer_3"],
        )
        return redirect("applications")

    return render(request, "pre_interview/applicant_form.html", {
        "pack": pack,
        "form": form,
    })
