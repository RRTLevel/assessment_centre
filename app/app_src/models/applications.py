import uuid

from django.contrib.auth.models import User
from django.db import models

from .question_bank import Category


class Pack(models.Model):
    """An assessment pack applicants apply to, with its pre-interview questions."""

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Interview questions for this pack come from its category's question bank.
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="packs",
        null=True,
        blank=True,
    )

    # Rich text (HTML) entered via the Summernote editor.
    pre_interview_question_1 = models.TextField(blank=True, null=True)
    pre_interview_question_2 = models.TextField(blank=True, null=True)
    pre_interview_question_3 = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PackGroup(models.Model):
    """A named collection of packs that applicants apply to in one submission."""

    name = models.CharField(max_length=255)
    packs = models.ManyToManyField(Pack, related_name="groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Application(models.Model):
    """One applicant's answers for one pack.

    A group submission creates one Application row per pack in the group,
    all sharing the same ``application_id`` and ``group``. Status, interview
    date and average score are kept in sync across the rows of a submission.
    """

    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_DENIED = "Denied"

    STATUS_CHOICES = [
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_ACCEPTED, STATUS_ACCEPTED),
        (STATUS_DENIED, STATUS_DENIED),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Shared by every row of one submission; not unique on its own.
    application_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    group = models.ForeignKey(
        PackGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="applications",
    )

    pack = models.ForeignKey(Pack, on_delete=models.CASCADE)

    answer_1 = models.TextField()
    answer_2 = models.TextField()
    answer_3 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    # Used by the inbox calendar.
    interview_date = models.DateTimeField(null=True, blank=True)

    # Average of the per-question interview scores, calculated on submit.
    average_score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("application_id", "pack")

    def __str__(self):
        return f"{self.user.username} - {self.application_id}"
