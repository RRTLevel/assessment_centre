import logging
from random import sample
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin

from .forms import AddNoteForm
from .models import Note


logger = logging.getLogger("")

class SignUpView(SuccessMessageMixin, CreateView):

    form_class = UserCreationForm
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

def interview(request):
    Questions =[
        "Tell me about yourself and your background.",
        "What are your greatest strengths and weaknesses?",
        "Why do you want to work for this company?",
        "Where do you see yourself in five years?",
        "Describe a challenging situation and how you overcame it.",
        "How do you handle working under pressure or tight deadlines?",
        "Tell me about a time you worked successfully in a team.",
        "What motivates you in your work?",
        "How do you prioritise tasks when managing multiple projects?",
        "Describe a time you made a mistake and how you handled it.",
        "What are your salary expectations?",
        "How do you stay up to date with industry trends?",
        "Tell me about a time you showed leadership.",
        "Why are you leaving your current position?",
        "Do you have any questions for us?"
            ]
    
    question_list = sample(Questions, 10)
    score = 10
    question_count = 1
    question_labels = []
    for i in range(len(question_list)):
        question_label = f"Question {question_count}: Score = {score}/ 10"
        question_labels.append(question_label)
        question_count += 1
        
    return render(
        request,
        "interview/interview.html",
        {"questions": question_list, "question_label": question_labels}
    )