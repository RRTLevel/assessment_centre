from django.db import models

from .applications import Application
from .question_bank import Indicator, Question

class InterviewResult(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="results",  # ← THIS is critical
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    feedback = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("application", "question")


class IndicatorScore(models.Model):
    """
    A per-indicator score recorded against one application's interview.
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="indicator_scores",
    )

    indicator = models.ForeignKey(
        Indicator,
        on_delete=models.CASCADE,
        related_name="scores",
    )

    score = models.PositiveSmallIntegerField(
        help_text="Score from 1–6"
    )

    class Meta:
        unique_together = ("application", "indicator")

    def __str__(self):
        return f"{self.application} | {self.indicator} | {self.score}"


class IndicatorGroupScore(models.Model):
    """
    An overall score and notes for one named indicator group.
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="indicator_group_scores",
    )

    group_name = models.CharField(max_length=100)

    score = models.PositiveSmallIntegerField(
        help_text="Score from 1–6"
    )

    notes = models.TextField(
        blank=True,
        default=""
    )

    class Meta:
        unique_together = ("application", "group_name")

    def __str__(self):
        return f"{self.application} | {self.group_name} | {self.score}"