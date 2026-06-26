import uuid
from django.db import models
from django.contrib.auth.models import User
from .validators import DomainUnicodeUsernameValidator


class DomainUser(User):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._meta.get_field('username').validators = [
            DomainUnicodeUsernameValidator()
        ]


class Note(models.Model):
    author = models.ForeignKey(DomainUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#where the system will gather the data for the form and be able to save it to a database
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Pack(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        related_name="packs",
        null=True,
        blank=True
    )
<<<<<<< Updated upstream
    pre_interview_question_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    pre_interview_question_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    pre_interview_question_3 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
=======

    pre_interview_question_1 = models.CharField(max_length=255, blank=True, null=True)
    pre_interview_question_2 = models.CharField(max_length=255, blank=True, null=True)
    pre_interview_question_3 = models.CharField(max_length=255, blank=True, null=True)
>>>>>>> Stashed changes

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

<<<<<<< Updated upstream
=======

class QuestionTable(models.Model):
    CATEGORY_CHOICES = [
        ("Category 1", "Category 1"),
        ("Category 2", "Category 2"),
        ("Category 3", "Category 3"),
        ("Category 4", "Category 4"),
    ]

    question = models.TextField()

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Category 1"
    )

    def __str__(self):
        return self.question


>>>>>>> Stashed changes
class Application(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Denied', 'Denied'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    application_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    pack = models.ForeignKey("Pack", on_delete=models.CASCADE)

    answer_1 = models.TextField()
    answer_2 = models.TextField()
    answer_3 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    # USED BY YOUR INBOX CALENDAR
    interview_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.application_id}"


class Questions(models.Model):
    text = models.TextField()
<<<<<<< Updated upstream
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')

=======

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='questions'
    )
>>>>>>> Stashed changes

    def __str__(self):
        return self.text[:60]


class InterviewResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
<<<<<<< Updated upstream
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
=======

    # FIXED: only ONE question field now
    question = models.ForeignKey(
        Questions,
        on_delete=models.CASCADE
    )

>>>>>>> Stashed changes
    score_1 = models.IntegerField(null=True, blank=True)
    score_2 = models.IntegerField(null=True, blank=True)
    score_3 = models.IntegerField(null=True, blank=True)

    notes = models.TextField(blank=True, default='')
    feedback = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
<<<<<<< Updated upstream
        unique_together = ('user', 'question')
=======
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.question}"
>>>>>>> Stashed changes
