from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    # =====================
    # HOME & STATIC PAGES
    # =====================
    path("", views.HomeView.as_view(), name="home"),
    path("documentation/", views.documentation_view, name="documentation"),
    path("help/", views.help_view, name="help"),

    # =====================
    # AUTH & ACCOUNTS
    # =====================
    path("login/", views.RememberMeLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("userprofile/", views.UserProfileView.as_view(), name="userprofile"),
    path("delete-account/", views.DeleteAccountView.as_view(), name="delete_account"),

    # =====================
    # QUESTION BANK
    # =====================
    path("add_questions/", views.add_question, name="add_questions"),
    path("questions/", views.question_list, name="question_list"),
    path("questions/delete/<int:pk>/", views.delete_question, name="delete_question"),
    path("ajax/load-questions/", views.load_questions, name="ajax_load_questions"),
    path("categories/", views.create_category, name="categories"),
    path("category/delete/<int:pk>/", views.delete_category, name="delete_category"),
    path("add_indicators/", views.add_indicators, name="add_indicators"),

    # =====================
    # PACKS & APPLICATIONS
    # =====================
    path("create-pack/", views.create_pack, name="create_pack"),
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
    path("accepted-applicants/", views.accepted_applicants, name="accepted_applicants"),

    # =====================
    # INTERVIEWS & INBOX
    # =====================
    path("interview/<uuid:application_id>/", views.start_interview, name="start_interview"),
    path("interview/<uuid:application_id>/autosave/", views.autosave_interview, name="autosave_interview"),
    path("inbox/", views.inbox_view, name="inbox"),

    # =====================
    # RESULTS & DASHBOARD
    # =====================
    path("results/", views.results_view, name="results"),
    path(
        "statistics_dashboard/candidate_dashboard/",
        views.candidate_dashboard,
        name="candidate_dashboard",
    ),
    path(
        "statistics_dashboard/candidate_dashboard/pdf/",
        views.candidate_dashboard_pdf,
        name="candidate_dashboard_pdf",
    ),

    # =====================
    # ERROR PAGES
    # =====================
    path("404/", views.Custom404View.as_view(), name="404"),
    path("500/", views.Custom500View.as_view(), name="500"),
]
