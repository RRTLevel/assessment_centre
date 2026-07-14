from django.db import models
from django.utils.html import strip_tags


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Rich text (HTML) entered via the Summernote editor.
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Questions(models.Model):
    # Rich text (HTML) entered via the Summernote editor.
    text = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    def __str__(self):
        return strip_tags(self.text)[:60]


class Indicator(models.Model):
    """A positive/negative behaviour pair, grouped under a shared name."""

    name = models.CharField(max_length=100)
    positive = models.TextField()
    negative = models.TextField()

    def __str__(self):
        return self.name
