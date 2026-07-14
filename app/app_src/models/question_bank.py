from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Questions(models.Model):
    text = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    def __str__(self):
        return self.text[:60]


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
