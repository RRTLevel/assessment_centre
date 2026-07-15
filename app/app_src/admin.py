from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .forms import DomainUserChangeForm
from .models import (
    Application,
    ApplicationPack,
    Category,
    DomainUser,
    Indicator,
    IndicatorGroupScore,
    IndicatorScore,
    InterviewResult,
    Note,
    Pack,
    PackGroup,
    Question,
)


class DomainUserAdmin(UserAdmin):
    form = DomainUserChangeForm
    list_display = ("username", "email", "account_types", "is_staff", "is_superuser", "is_active")
    list_filter = ("groups", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    @admin.display(description="Account type")
    def account_types(self, obj):
        groups = obj.groups.values_list("name", flat=True)
        return ", ".join(groups) or "None"


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "pub_date")
    list_filter = ("pub_date",)
    search_fields = ("title", "body", "author__username", "author__email")
    date_hierarchy = "pub_date"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name", "description")


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("title", "description", "category__name")
    date_hierarchy = "created_at"


@admin.register(PackGroup)
class PackGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    filter_horizontal = ("packs",)
    search_fields = ("name", "packs__title")
    date_hierarchy = "created_at"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "category")
    list_filter = ("category",)
    search_fields = ("text", "category__name")

    @admin.display(description="Question")
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("name", "short_positive", "short_negative")
    list_filter = ("name",)
    search_fields = ("name", "positive", "negative")

    @admin.display(description="Positive")
    def short_positive(self, obj):
        return obj.positive[:80]

    @admin.display(description="Negative")
    def short_negative(self, obj):
        return obj.negative[:80]


@admin.register(IndicatorScore)
class IndicatorScoreAdmin(admin.ModelAdmin):
    list_display = ("application", "indicator", "score")
    list_filter = ("score", "indicator__name")
    search_fields = ("application__user__username", "application__user__email", "indicator__name")
    list_select_related = ("application", "indicator")


@admin.register(IndicatorGroupScore)
class IndicatorGroupScoreAdmin(admin.ModelAdmin):
    list_display = ("application", "group_name", "score")
    list_filter = ("score", "group_name")
    search_fields = ("application__user__username", "application__user__email", "group_name", "notes")
    list_select_related = ("application",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("application_id", "user", "pack", "status", "interview_date", "average_score", "created_at")
    list_filter = ("status", "pack", "created_at", "interview_date")
    search_fields = ("application_id", "user__username", "user__email", "pack__title")
    readonly_fields = ("application_id", "created_at", "average_score")
    date_hierarchy = "created_at"
    list_select_related = ("user", "pack")


@admin.register(InterviewResult)
class InterviewResultAdmin(admin.ModelAdmin):
    list_display = ("application", "question", "score", "updated_at")
    list_filter = ("score", "updated_at", "question__category")
    search_fields = ("application__user__username", "application__user__email", "question__text", "notes", "feedback")
    date_hierarchy = "updated_at"
    list_select_related = ("application", "question")


@admin.register(ApplicationPack)
class ApplicationPackAdmin(admin.ModelAdmin):
    list_display = ("application", "pack", "order")
    list_filter = ("pack",)
    search_fields = (
        "application__application_id",
        "application__user__username",
        "application__user__email",
        "pack__title",
    )
    list_select_related = ("application", "pack")


admin.site.unregister(User)
admin.site.register(DomainUser, DomainUserAdmin)
