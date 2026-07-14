from django.db import models

from .applications import Application, Pack
from .question_bank import Indicator, Questions


class ApplicationPack(models.Model):
    """An assessment pack assigned to a specific application, with ordering."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interview_packs",
    )
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("application", "pack")

    def __str__(self):
        return f"{self.application} — {self.pack}"


class InterviewResult(models.Model):
    """A scored answer for one applicant (Application) and one interview question."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="results",
    )
    question = models.ForeignKey(Questions, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    feedback = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)
    application_pack = models.ForeignKey(
        ApplicationPack,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="results",
    )

    class Meta:
        unique_together = ("application", "question")

    def __str__(self):
        return f"{self.application.user.username} - {self.question} ({self.score})"


class IndicatorScore(models.Model):
    """A per-indicator score recorded against one application's interview."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="indicator_scores",
    )
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        unique_together = ("application", "indicator")


class IndicatorGroupScore(models.Model):
    """An overall score and notes for one named indicator group."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="indicator_group_scores",
    )
    group_name = models.CharField(max_length=100)
    score = models.IntegerField()
    notes = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("application", "group_name")
