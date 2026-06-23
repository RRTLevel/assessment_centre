import logging
from random import sample
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .forms import AddNoteForm, DomainUserCreationForm, PackForm, ApplicantForm, CategoryForm
from .models import Note, Pack, QuestionTable, Application

logger = logging.getLogger("")


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
    success_message = "Your account has been created! Please login:"
    template_name = "registration/signup.html"


class userprofileView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    model = Note
    template_name = 'notes/userprofile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = settings.APPLICATION_NAME + ' - Profile'

        user = self.request.user
        group = self.request.user.groups.first()
        context["AccountType"] = group

        return context

    def post(self, request, **kwargs):
        user = request.user
        old_pass = request.POST.get("old_password")
        new_pass1 = request.POST.get("new_password1")
        new_pass2 = request.POST.get("new_password2")

        if not user.check_password(old_pass):
            messages.error(request, "Your current password was entered incorrectly.", extra_tags="danger")
            return redirect("userprofile")

        if new_pass1 != new_pass2:
            messages.error(request, "The two new password fields didn't match.", extra_tags="danger")
            return redirect("userprofile")

        if len(new_pass1) < 8:
            messages.error(request, "Your new password must be at least 8 characters long.", extra_tags="danger")
            return redirect("userprofile")

        user.set_password(new_pass1)
        user.save()
        update_session_auth_hash(request, user)

        messages.success(request, "Your password was successfully updated!", extra_tags="success")
        return redirect("userprofile")

        
        return context


class homeView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    form_class = AddNoteForm
    model = Note
    template_name = 'notes/notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home"] = True
        context["page_title"] = settings.APPLICATION_NAME + ' - Notes'
        context["notes"] = Note.objects.order_by('-pub_date')[:5]
        return context

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        logger.info(f"{self.request.user} successfully posted a note.")
        return super(homeView, self).form_valid(form)


def documentationView(request):
    context = {
        'page_title': settings.APPLICATION_NAME + ' - User Guide',
        'documentation': True,
    }
    return render(request, 'notes/documentation.html', context)


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"


@login_required(login_url='/login')
def applications(request):
    packs = Pack.objects.all().order_by('-created_at')
    return render(request, "pre_interview/applications.html", {
        "packs": packs,
        "applications_active": True
    })


@login_required(login_url='/login')
def create_pack(request):
    if request.method == "POST":
        form = PackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('applications')
    else:
        form = PackForm()

    return render(request, "pre_interview/create_pack.html", {
        "form": form,
        "create_pack_active": True
    })


@login_required(login_url='/login')
def interview(request):
    questions = QuestionTable.objects.all()
    return render(request, "interview/interview.html", {
        "questions": questions,
        "interview": True
    })


@login_required(login_url='/login')
def applicant_form(request, pack_id):
    pack = get_object_or_404(Pack, id=pack_id)

    if request.method == "POST":
        form = ApplicantForm(request.POST)

        if form.is_valid():
            answers = form.cleaned_data

            Application.objects.create(
                user=request.user,
                pack=pack,
                answer_1=answers["answer_1"],
                answer_2=answers["answer_2"],
                answer_3=answers["answer_3"],
            )
            return redirect("applications")
    else:
        form = ApplicantForm()

    return render(
        request,
        "pre_interview/applicant_form.html",
        {
            "pack": pack,
            "form": form,
        }
    )

def add_questions(request):
    return render(request, "add_questions/add_questions.html")

@login_required(login_url='/login')
def application_review(request):
    applications = Application.objects.all().select_related('user', 'pack')
    return render(request, "pre_interview/application_review.html", {
        "applications": applications
    })


def create_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('applications')
    else:
        form = CategoryForm()

    return render(request, "pre_interview/create_category.html", {"form": form})


def approve_application(request, id):
    app = Application.objects.get(id=id)
    app.status = "approved"
    app.save()
    return redirect("applications_review")


def deny_application(request, id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=id)
        application.delete()
    return redirect("applications_review")


def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)

    return render(request, "pre_interview/view_more.html", {
        "application": application
    })

