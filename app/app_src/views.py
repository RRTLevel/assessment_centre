import logging

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .forms import AddNoteForm, DomainUserCreationForm
from .models import Note
from .forms import PackForm
from .models import Pack
from .models import QuestionTable
from .forms import ApplicantForm
from .models import Application

from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View


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

        logger.info(f"{self.request.user} sucessfully posted a note.")

        return super(homeView, self).form_valid(form)


def documentationView(request):

    context = {
        'page_title' : settings.APPLICATION_NAME + ' - User Guide',
        'documentation': True,
    }

    return render(request, 'notes/documentation.html',context)


class Custom404View(TemplateView):

    template_name = "404.html"


class Custom500View(TemplateView):

    template_name = "500.html"

def applications(request):
    packs = Pack.objects.all().order_by('-created_at')
    return render(request, "pre_interview/applications.html", {"packs": packs})

def create_pack(request):
    if request.method == "POST":
        form = PackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('applications') 
    else:
        form = PackForm()

    return render(request, "pre_interview/create_pack.html", {"form": form})


def interview(request):

    questions = QuestionTable.objects.all()

    return render(request, "interview/interview.html",
        {"questions": questions})

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

def application_review(request):
    applications = Application.objects.all().select_related('user', 'pack')

    return render(request, "pre_interview/application_review.html", {
        "applications": applications
    })