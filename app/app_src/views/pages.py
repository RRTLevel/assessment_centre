"""The notes home page, static pages and error pages."""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from ..forms import AddNoteForm
from ..models import Note


class HomeView(LoginRequiredMixin, CreateView):
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


def documentation_view(request):
    return render(request, "notes/documentation.html")


def help_view(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"
