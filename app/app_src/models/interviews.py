from django.db import models

from .applications import Application, Pack
from .question_bank import Indicator, Question


class ApplicationPack(models.Model):
    """A pack chosen for one application's interview, with ordering.

    Rows are created when the interview is scheduled (or default to the
    submission's packs) and hang off the submission's primary Application.
    """

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
    """Score, notes and feedback recorded for one question in one interview."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="results",
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    # Rich text (HTML) entered via the Summernote editor.
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


class IndicatorScore(models.Model):
    """A per-behaviour-pair score recorded against one application's interview."""

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
    score = models.PositiveSmallIntegerField(help_text="Score from 1–6")

    class Meta:
        unique_together = ("application", "indicator")

    def __str__(self):
        return f"{self.application} | {self.indicator} | {self.score}"


class IndicatorGroupScore(models.Model):
    """An overall score and notes for one named indicator group."""

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="indicator_group_scores",
    )
    group_name = models.CharField(max_length=100)
    score = models.PositiveSmallIntegerField(help_text="Score from 1–6")
    # Rich text (HTML) entered via the Summernote editor.
    notes = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("application", "group_name")

    def __str__(self):
        return f"{self.application} | {self.group_name} | {self.score}"
