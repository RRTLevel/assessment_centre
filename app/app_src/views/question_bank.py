"""Managing the question bank: categories, questions and indicators."""

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import strip_tags

from ..forms import CategoryForm, GenreForm, QuestionForm
from ..models import Category, Genre, Indicator, Questions
from ..forms import CategoryForm, QuestionForm
from ..models import Category, Indicator, Question
from ..permissions import ASSESSOR_GROUP, group_required


@login_required
@group_required(ASSESSOR_GROUP)
def add_question(request):
    form = QuestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.cleaned_data["category"]
        for text in form.question_texts():
            Question.objects.create(text=text, category=category)

        return redirect("add_questions")

    questions = Question.objects.select_related("category").order_by("-id")
    return render(request, "add_questions/add_questions.html", {
        "form": form,
        "questions": questions,
        "add_question": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def question_list(request):
    questions = Question.objects.select_related("category").order_by("-id")
    return render(request, "add_questions/question_list.html", {
        "questions": questions,
        "add_question": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def delete_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        question.delete()
    return redirect("question_list")


@login_required
def load_questions(request):
    """AJAX endpoint: the questions belonging to the selected category."""
    category_id = request.GET.get("category")

    if not category_id:
        return JsonResponse([], safe=False)

    # Question text is rich HTML; <option> labels can only show plain text,
    # so the page script gets both (the HTML fills the pack's editors).
    questions = Question.objects.filter(category_id=category_id)
    data = [{"id": q.id, "text": strip_tags(q.text), "html": q.text} for q in questions]
    return JsonResponse(data, safe=False)


@login_required
@group_required(ASSESSOR_GROUP)
def create_category(request):
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("categories")

    return render(request, "pre_interview/create_category.html", {
        "form": form,
        "categories": Category.objects.annotate(q_count=Count("questions")),
    })


@login_required
@group_required(ASSESSOR_GROUP)
def delete_category(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == "POST":
        category.delete()
    return redirect("categories")


@login_required
@group_required(ASSESSOR_GROUP)
def add_indicators(request):
    """Manage named groups of positive/negative indicator pairs."""
    if request.method == "POST":
        if "delete_indicator" in request.POST:
            Indicator.objects.filter(id=request.POST.get("indicator_id")).delete()
            return redirect("add_indicators")

        if "delete_by_name" in request.POST:
            Indicator.objects.filter(name=request.POST.get("indicator_name")).delete()
            return redirect("add_indicators")

        _save_indicator_group(request.POST)
        return redirect("add_indicators")

    all_indicators = Indicator.objects.order_by("name", "id")
    indicator_names = list(
        Indicator.objects.values_list("name", flat=True).distinct().order_by("name")
    )

    grouped = {}
    for indicator in all_indicators:
        grouped.setdefault(indicator.name, []).append(indicator)

    return render(request, "indicators/add_indicators.html", {
        "page_title": settings.APPLICATION_NAME + " - Add Indicators",
        "indicator_names": indicator_names,
        "grouped_indicators": grouped,
    })


def _save_indicator_group(post_data):
    """Create the submitted positive/negative pairs under one group name.

    In "replace" mode the group's existing pairs are deleted first.
    """
    name = post_data.get("indicator_name", "").strip()
    mode = post_data.get("mode", "add")

    pairs = []
    for key in post_data:
        if key.startswith("positive_"):
            index = key[len("positive_"):]
            positive = post_data.get(key, "").strip()
            negative = post_data.get(f"negative_{index}", "").strip()
            if positive or negative:
                pairs.append((positive, negative))

    if not name or not pairs:
        return

    if mode == "replace":
        Indicator.objects.filter(name=name).delete()

    for positive, negative in pairs:
        Indicator.objects.create(name=name, positive=positive, negative=negative)


@login_required
@group_required(ASSESSOR_GROUP)
def manage_genres(request):
    """Create and delete interview genres (each bundles 3 packs)."""
    error = None
    if request.method == "POST":
        if "delete_genre" in request.POST:
            Genre.objects.filter(id=request.POST.get("genre_id")).delete()
            return redirect("manage_genres")

        form = GenreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manage_genres")
        else:
            error = "Please fix the errors below."
    else:
        form = GenreForm()

    return render(request, "genres/manage_genres.html", {
        "form": form,
        "genres": Genre.objects.select_related("pack_1", "pack_2", "pack_3").all(),
        "error": error,
    })
