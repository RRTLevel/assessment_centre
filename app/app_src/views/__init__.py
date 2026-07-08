"""Views, grouped by domain.

Everything is re-exported here so ``urls.py`` and callers can keep using
``from app_src.views import <view>``.
"""

from .accounts import (
    DeleteAccountView,
    RememberMeLoginView,
    SignUpView,
    UserProfileView,
)
from .applications import (
    accepted_applicants,
    applicant_form,
    application_detail,
    application_review,
    applications,
    approve_application,
    create_pack,
    deny_application,
)
from .dashboard import candidate_dashboard, candidate_dashboard_pdf, results_view
from .interviews import inbox_view, start_interview
from .pages import (
    Custom404View,
    Custom500View,
    HomeView,
    documentation_view,
    help_view,
)
from .question_bank import (
    add_indicators,
    add_question,
    create_category,
    delete_category,
    delete_question,
    load_questions,
    question_list,
)

__all__ = [
    "Custom404View",
    "Custom500View",
    "DeleteAccountView",
    "HomeView",
    "RememberMeLoginView",
    "SignUpView",
    "UserProfileView",
    "accepted_applicants",
    "add_indicators",
    "add_question",
    "applicant_form",
    "application_detail",
    "application_review",
    "applications",
    "approve_application",
    "candidate_dashboard",
    "candidate_dashboard_pdf",
    "create_category",
    "create_pack",
    "delete_category",
    "delete_question",
    "deny_application",
    "documentation_view",
    "help_view",
    "inbox_view",
    "load_questions",
    "question_list",
    "results_view",
    "start_interview",
]
