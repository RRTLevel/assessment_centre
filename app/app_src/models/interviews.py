from django.db import models

from .applications import Application
from .question_bank import Indicator, Questions


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

    class Meta:
        unique_together = ("application", "question")

    def __str__(self):
        return f"{self.application.user.username} - {self.question} ({self.score})"


class IndicatorScore(models.Model):
    """A per-indicator score recorded against one interview result."""

    result = models.ForeignKey(
        InterviewResult,
        on_delete=models.CASCADE,
        related_name="indicator_scores",
    )
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        unique_together = ("result", "indicator")
