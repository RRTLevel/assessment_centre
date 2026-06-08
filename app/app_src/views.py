import logging

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
