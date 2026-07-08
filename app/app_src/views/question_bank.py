"""Managing the question bank: categories, questions and indicators."""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CategoryForm, IndicatorForm, QuestionForm
from ..models import Category, Indicator, Questions
from ..permissions import ASSESSOR_GROUP, group_required


@login_required
@group_required(ASSESSOR_GROUP)
def add_question(request):
    form = QuestionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.cleaned_data["category"]
        for text in form.question_texts():
            Questions.objects.create(text=text, category=category)

        return redirect("add_questions")

    questions = Questions.objects.select_related("category").order_by("-id")
    return render(request, "add_questions/add_questions.html", {
        "form": form,
        "questions": questions,
        "add_question": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def question_list(request):
    questions = Questions.objects.select_related("category").order_by("-id")
    return render(request, "add_questions/question_list.html", {
        "questions": questions,
        "add_question": True,
    })


@login_required
@group_required(ASSESSOR_GROUP)
def delete_question(request, pk):
    question = get_object_or_404(Questions, pk=pk)
    if request.method == "POST":
        question.delete()
    return redirect("question_list")


@login_required
def load_questions(request):
    """AJAX endpoint: the questions belonging to the selected category."""
    category_id = request.GET.get("category")

    if not category_id:
        return JsonResponse([], safe=False)

    questions = Questions.objects.filter(category_id=category_id).values("id", "text")
    return JsonResponse(list(questions), safe=False)


@login_required
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
    if request.method == "POST" and "delete_indicator" in request.POST:
        Indicator.objects.filter(id=request.POST.get("indicator_id")).delete()
        return redirect("add_indicators")

    indicator = None
    if "edit" in request.GET:
        indicator = get_object_or_404(Indicator, id=request.GET["edit"])

    form = IndicatorForm(request.POST or None, instance=indicator)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("add_indicators")

    return render(request, "indicators/add_indicators.html", {
        "form": form,
        "indicators": Indicator.objects.all(),
    })
