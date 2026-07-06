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


# where the system will gather the data for the form and be able to save it to a database
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

    pre_interview_question_1 = models.CharField(max_length=255, blank=True, null=True)
    pre_interview_question_2 = models.CharField(max_length=255, blank=True, null=True)
    pre_interview_question_3 = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


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

    # Average of the per-question interview scores, calculated on submit.
    average_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.application_id}"


class Questions(models.Model):
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')


    def __str__(self):
        return self.text[:60]

class Indicator(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="indicators"
    )

    name = models.CharField(max_length=100)

    positive = models.TextField()
    negative = models.TextField()

    def __str__(self):
        return self.name
class IndicatorScore(models.Model):
    result = models.ForeignKey('InterviewResult', on_delete=models.CASCADE, related_name='indicator_scores')
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        unique_together = ('result', 'indicator')

class InterviewResult(models.Model):
    """A scored answer for one applicant (Application) and one interview question."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE,related_name="results")
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    feedback = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('application', 'question')

    def __str__(self):
        return f"{self.application.user.username} - {self.question} ({self.score})"

