from django.db import models

from .users import DomainUser


class Note(models.Model):
    author = models.ForeignKey(DomainUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
