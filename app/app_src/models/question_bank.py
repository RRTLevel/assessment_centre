from django.db import models
from django.utils.html import strip_tags


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Rich text (HTML) entered via the Summernote editor.
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Question(models.Model):
    # Rich text (HTML) entered via the Summernote editor.
    text = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    class Meta:
        # Historical table name, kept from when the model was called "Questions".
        db_table = "app_src_questions"

    def __str__(self):
        return strip_tags(self.text)[:60]


class Genre(models.Model):
    """A named programme that groups exactly 3 interview packs together.

    During an interview the assessor works through all three packs and can
    switch between them via tabs.
    """

    name = models.CharField(max_length=100, unique=True)
    pack_1 = models.ForeignKey(
        "app_src.Pack",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="genres_as_slot_1",
    )
    pack_2 = models.ForeignKey(
        "app_src.Pack",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="genres_as_slot_2",
    )
    pack_3 = models.ForeignKey(
        "app_src.Pack",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="genres_as_slot_3",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def packs(self):
        """Return the list of non-null packs in slot order."""
        return [p for p in (self.pack_1, self.pack_2, self.pack_3) if p]


class Indicator(models.Model):
    """A positive/negative behaviour pair, grouped under a shared name."""

    name = models.CharField(max_length=100)
    positive = models.TextField()
    negative = models.TextField()

    def __str__(self):
        return self.name
