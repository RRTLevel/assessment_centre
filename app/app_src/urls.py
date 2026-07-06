from django.urls import path

from . import views
from .views import DeleteAccountView, RememberMeLoginView

urlpatterns = [
    # =====================
    # HOME
    # =====================
    path("", views.homeView.as_view(), name="home"),

    # =====================
    # AUTH
    # =====================
    path("login/", RememberMeLoginView.as_view(), name="login"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("userprofile/", views.userprofileView.as_view(), name="userprofile"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete_account"),

    # =====================
    # STATIC PAGES
    # =====================
    path("documentation/", views.documentationView, name="documentation"),
    path("help/", views.helpView, name="help"),

    # =====================
    # RESULTS
    # =====================
    path("results/", views.resultsView, name="results"),
    path(
        "statistics_dashboard/candidate_dashboard/",
        views.candidate_dashboard,
        name="candidate_dashboard",
    ),

    # =====================
    # INDICATORS
    # =====================
    path("add_indicators/", views.add_indicators, name="add_indicators"),

    # =====================
    # QUESTIONS
    # =====================
    path("add_questions/", views.add_question, name="add_questions"),
    path("questions/", views.question_list, name="question_list"),
    path("questions/delete/<int:pk>/", views.delete_question, name="delete_question"),
    path("ajax/load-questions/", views.load_questions, name="ajax_load_questions"),

    # =====================
    # CATEGORIES
    # =====================
    path("categories/", views.create_category, name="categories"),
    path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),

    # =====================
    # PACKS
    # =====================
    path("create-pack/", views.create_pack, name="create_pack"),

    # =====================
    # APPLICATIONS
    # =====================
    path("applications/", views.applications, name="applications"),
    path("applicant-form/<int:pack_id>/", views.applicant_form, name="applicant_form"),
    path("application-review/", views.application_review, name="application_review"),
    path(
        "application-review/<uuid:application_id>/",
        views.application_detail,
        name="application_detail",
    ),
    path(
        "applications/<uuid:application_id>/approve/",
        views.approve_application,
        name="approve_application",
    ),
    path(
        "applications/<uuid:application_id>/deny/",
        views.deny_application,
        name="deny_application",
    ),
    path(
        "accepted-applicants/",
        views.accepted_applicants,
        name="accepted_applicants",
    ),

    # =====================
    # INTERVIEWS
    # =====================
    path(
        "interview/<uuid:application_id>/",
        views.start_interview,
        name="start_interview",
    ),

    # =====================
    # INBOX
    # =====================
    path("inbox/", views.inbox_view, name="inbox"),

    # =====================
    # ERROR PAGES
    # =====================
    path("404/", views.Custom404View.as_view(), name="404"),
    path("500/", views.Custom500View.as_view(), name="500"),
]