import uuid

from django.contrib.auth.models import User
from django.db import models

from .question_bank import Category
from django.utils import timezone


from django.db import models

class Pack(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    pre_interview_question_1 = models.TextField(blank=True, null=True)
    pre_interview_question_2 = models.TextField(blank=True, null=True)
    pre_interview_question_3 = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    # Rich text (HTML) entered via the Summernote editor.
    pre_interview_question_1 = models.TextField(blank=True, null=True)
    pre_interview_question_2 = models.TextField(blank=True, null=True)
    pre_interview_question_3 = models.TextField(blank=True, null=True)

class PackGroup(models.Model):
    name = models.CharField(max_length=255)
    packs = models.ManyToManyField(Pack, related_name="groups")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Application(models.Model):

    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_DENIED = "Denied"

    STATUS_CHOICES = [
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_ACCEPTED, STATUS_ACCEPTED),
        (STATUS_DENIED, STATUS_DENIED),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    group = models.ForeignKey(
        PackGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="applications"
    )

    application_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
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

    interview_date = models.DateTimeField(
        null=True,
        blank=True
    )

    average_score = models.FloatField(
    null=True,
    blank=True
)

def __str__(self):
    return f"{self.user.username} - {self.application_id}"