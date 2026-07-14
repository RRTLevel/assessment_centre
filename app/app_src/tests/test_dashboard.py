from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import (
    Application,
    Category,
    IndicatorScore,
    Indicator,
    InterviewResult,
    Pack,
    PackGroup,
    Question,
)


class ScoredInterviewFixture:
    """One candidate in a group with two scored responses across two questions."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "a@a.com", "pw")

        category = Category.objects.create(name="General")
        pack = Pack.objects.create(
            title="Pack 1",
            description="d",
            category=category,
            pre_interview_question_1="Why do you want this placement?",
            pre_interview_question_2="What are your strengths?",
        )
        cls.group = PackGroup.objects.create(name="Placement Scheme")
        cls.group.packs.set([pack])

        cls.q1 = Question.objects.create(text="Tell us about yourself", category=category)
        cls.q2 = Question.objects.create(text="Why this role?", category=category)

        candidate = User.objects.create_user("candidate", password="pw")
        cls.application = Application.objects.create(
            user=candidate,
            pack=pack,
            group=cls.group,
            answer_1="I want to learn on real projects.",
            answer_2="Organisation and communication.",
            answer_3="",
            average_score=4.0,
        )

        InterviewResult.objects.create(
            application=cls.application,
            question=cls.q1,
            score=6,
            notes="Gave a confident, structured answer.",
            feedback="Strong communicator.",
        )
        InterviewResult.objects.create(application=cls.application, question=cls.q2, score=2)

        indicator = Indicator.objects.create(
            name="Communication", positive="Clear", negative="Rambles",
        )
        IndicatorScore.objects.create(
            application=cls.application, indicator=indicator, score=5,
        )

    def setUp(self):
        self.client.force_login(self.admin)


class CandidateDashboardTest(ScoredInterviewFixture, TestCase):
    def test_dashboard_shows_group_and_scores(self):
        response = self.client.get(reverse("candidate_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "candidate")
        self.assertContains(response, "Placement Scheme")
        self.assertContains(response, "Download PDF")
        self.assertContains(response, reverse("candidate_dashboard_pdf"))


class CandidateDashboardPdfTest(ScoredInterviewFixture, TestCase):
    def test_pdf_download(self):
        response = self.client.get(reverse("candidate_dashboard_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_pdf_download_with_filters(self):
        response = self.client.get(
            reverse("candidate_dashboard_pdf"),
            {"from": "2020-01-01", "to": "2030-01-01", "sort": "lowest"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_pdf_download_no_results(self):
        InterviewResult.objects.all().delete()
        response = self.client.get(reverse("candidate_dashboard_pdf"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.startswith(b"%PDF"))


class ResultsPageTest(ScoredInterviewFixture, TestCase):
    def test_results_page_shows_candidate_results_by_pack(self):
        response = self.client.get(reverse("results"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 interviewed candidate")
        self.assertContains(response, "candidate")
        self.assertContains(response, "Placement Scheme")
        self.assertContains(response, "Pack 1")
        self.assertContains(response, self.q1.text)
        self.assertContains(response, self.q2.text)
        self.assertContains(response, "Gave a confident, structured answer.")
        self.assertContains(response, "Strong communicator.")

    def test_results_page_shows_indicator_scores(self):
        response = self.client.get(reverse("results"))
        self.assertContains(response, "Interview Assessment")
        self.assertContains(response, "Communication")

    def test_results_page_empty_state(self):
        InterviewResult.objects.all().delete()
        response = self.client.get(reverse("results"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No results to display yet.")
