from django.db import models
from django.contrib.auth.models import User

from .validators import DomainUnicodeUsernameValidator


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
    pub_date = models.DateTimeField('date_published', auto_now_add=True, blank=True)

    def __str__(self):
        return self.title

