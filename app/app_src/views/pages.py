"""The notes home page, static pages and error pages."""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from ..forms import AddNoteForm
from ..models import Note


def HomeView(request):

    return render(request, "home.html")


def documentation_view(request):
    return render(request, "notes/documentation.html")


def help_view(request):
    return render(request, "help/help.html")


class Custom404View(TemplateView):
    template_name = "404.html"


class Custom500View(TemplateView):
    template_name = "500.html"
