from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import (
    Application,
    Category,
    Indicator,
    IndicatorGroupScore,
    IndicatorScore,
    InterviewResult,
    Pack,
    Questions,
)


class StartInterviewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "a@a.com", "pw")

        category = Category.objects.create(name="General")
        pack = Pack.objects.create(title="Pack 1", description="d", category=category)

        cls.question = Questions.objects.create(text="Tell us about yourself", category=category)
        cls.indicator = Indicator.objects.create(
            name="Communication",
            positive="Communicates clearly",
            negative="Rambles without structure",
        )

        candidate = User.objects.create_user("candidate", password="pw")
        cls.application = Application.objects.create(
            user=candidate,
            pack=pack,
            answer_1="a1",
            answer_2="a2",
            answer_3="a3",
            status=Application.STATUS_ACCEPTED,
        )

    def setUp(self):
        self.client.force_login(self.admin)

    def interview_url(self):
        return reverse("start_interview", args=[self.application.application_id])

    def test_interview_page_renders(self):
        response = self.client.get(self.interview_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.text)
        self.assertContains(response, "Communication")

    def test_submitting_scores_saves_results_and_average(self):
        response = self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "5",
            f"notes_{self.question.id}": "Clear and confident.",
            f"feedback_{self.question.id}": "Well done.",
            f"indicator_score_{self.indicator.id}": "4",
            "group_score_Communication": "3",
            "group_notes_Communication": "Generally strong.",
        })
        self.assertRedirects(response, reverse("inbox"))

        result = InterviewResult.objects.get(application=self.application, question=self.question)
        self.assertEqual(result.score, 5)
        self.assertEqual(result.notes, "Clear and confident.")
        self.assertEqual(result.feedback, "Well done.")

        indicator_score = IndicatorScore.objects.get(
            application=self.application, indicator=self.indicator,
        )
        self.assertEqual(indicator_score.score, 4)

        group_score = IndicatorGroupScore.objects.get(
            application=self.application, group_name="Communication",
        )
        self.assertEqual(group_score.score, 3)
        self.assertEqual(group_score.notes, "Generally strong.")

        self.application.refresh_from_db()
        self.assertEqual(self.application.average_score, 5.0)

    def test_resubmitting_updates_existing_scores(self):
        self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "2",
            f"indicator_score_{self.indicator.id}": "2",
            "group_score_Communication": "2",
        })
        self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "6",
            f"indicator_score_{self.indicator.id}": "6",
            "group_score_Communication": "6",
        })

        self.assertEqual(InterviewResult.objects.count(), 1)
        self.assertEqual(IndicatorScore.objects.count(), 1)
        self.assertEqual(IndicatorGroupScore.objects.count(), 1)
        self.assertEqual(InterviewResult.objects.get().score, 6)
        self.assertEqual(IndicatorScore.objects.get().score, 6)
        self.assertEqual(IndicatorGroupScore.objects.get().score, 6)


class AddIndicatorsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "a@a.com", "pw")

    def setUp(self):
        self.client.force_login(self.admin)

    def test_creating_a_named_group_of_pairs(self):
        response = self.client.post(reverse("add_indicators"), {
            "indicator_name": "Teamwork",
            "positive_1": "Listens to others",
            "negative_1": "Talks over people",
            "positive_2": "Shares credit",
            "negative_2": "",
        })
        self.assertRedirects(response, reverse("add_indicators"))

        pairs = Indicator.objects.filter(name="Teamwork").order_by("id")
        self.assertEqual(pairs.count(), 2)
        self.assertEqual(pairs[0].positive, "Listens to others")
        self.assertEqual(pairs[1].positive, "Shares credit")

    def test_replace_mode_overwrites_existing_group(self):
        Indicator.objects.create(name="Teamwork", positive="Old", negative="Old")

        self.client.post(reverse("add_indicators"), {
            "indicator_name": "Teamwork",
            "mode": "replace",
            "positive_1": "New positive",
            "negative_1": "New negative",
        })

        pairs = Indicator.objects.filter(name="Teamwork")
        self.assertEqual(pairs.count(), 1)
        self.assertEqual(pairs.get().positive, "New positive")

    def test_delete_by_name_removes_whole_group(self):
        Indicator.objects.create(name="Teamwork", positive="p", negative="n")
        Indicator.objects.create(name="Teamwork", positive="p2", negative="n2")

        self.client.post(reverse("add_indicators"), {
            "delete_by_name": "1",
            "indicator_name": "Teamwork",
        })

        self.assertFalse(Indicator.objects.filter(name="Teamwork").exists())
