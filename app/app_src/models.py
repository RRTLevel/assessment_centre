from django.db import models
from django.contrib.auth.models import User

from .validators import DomainUnicodeUsernameValidator
import uuid


class DomainUser(User):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):

        self._meta.get_field(
            'username'
        ).validators[0] = DomainUnicodeUsernameValidator()

        super().__init__(*args, **kwargs)


class Note(models.Model):

    author = models.ForeignKey(DomainUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField(
        'date_published',
        auto_now_add=True,
        blank=True
    )

    def __str__(self):
        return self.title

#where the system will gather the data for the form and be able to save it to a database
from django.db import models


class Pack(models.Model):

    class PackClass(models.TextChoices):
        APPRENTICE = "apprentice", "Apprentice"
        STAFF = "staff", "Staff"
        MANAGER = "manager", "Manager"

    title = models.CharField(max_length=200)
    description = models.TextField()

    pack_class = models.CharField(
        max_length=20,
        choices=PackClass.choices,
        default=PackClass.APPRENTICE
    )

    pre_interview_question_1 = models.CharField(max_length=255, blank=True)
    pre_interview_question_2 = models.CharField(max_length=255, blank=True)
    pre_interview_question_3 = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    application_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    pack = models.ForeignKey("Pack", on_delete=models.CASCADE)

    answer_1 = models.TextField()
    answer_2 = models.TextField()
    answer_3 = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.application_id}"