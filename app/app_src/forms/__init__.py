"""Forms, grouped by domain.

Everything is re-exported here so callers can keep using
``from app_src.forms import <Form>``.
"""

from .accounts import ACCOUNT_TYPE_CHOICES, DomainUserChangeForm, DomainUserCreationForm
from .applications import ApplicantForm, PackForm
from .notes import AddNoteForm
from .question_bank import CategoryForm, QuestionForm

__all__ = [
    "ACCOUNT_TYPE_CHOICES",
    "AddNoteForm",
    "ApplicantForm",
    "CategoryForm",
    "DomainUserChangeForm",
    "DomainUserCreationForm",
    "PackForm",
    "QuestionForm",
]
