from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import (
    Application,
    Category,
    Indicator,
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
            question=cls.question,
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

    def test_submitting_scores_saves_results_and_average(self):
        response = self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "5",
            f"notes_{self.question.id}": "Clear and confident.",
            f"feedback_{self.question.id}": "Well done.",
            f"indicator_score_{self.question.id}_{self.indicator.id}": "4",
        })
        self.assertRedirects(response, reverse("inbox"))

        result = InterviewResult.objects.get(application=self.application, question=self.question)
        self.assertEqual(result.score, 5)
        self.assertEqual(result.notes, "Clear and confident.")
        self.assertEqual(result.feedback, "Well done.")

        indicator_score = IndicatorScore.objects.get(result=result, indicator=self.indicator)
        self.assertEqual(indicator_score.score, 4)

        self.application.refresh_from_db()
        self.assertEqual(self.application.average_score, 5.0)

    def test_resubmitting_updates_existing_result(self):
        self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "2",
            f"indicator_score_{self.question.id}_{self.indicator.id}": "2",
        })
        self.client.post(self.interview_url(), {
            f"overall_score_{self.question.id}": "6",
            f"indicator_score_{self.question.id}_{self.indicator.id}": "6",
        })

        self.assertEqual(InterviewResult.objects.count(), 1)
        self.assertEqual(IndicatorScore.objects.count(), 1)
        self.assertEqual(InterviewResult.objects.get().score, 6)
        self.assertEqual(IndicatorScore.objects.get().score, 6)
