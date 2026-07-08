from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Application, Category, InterviewResult, Pack, Questions


class CandidateDashboardPdfTest(TestCase):
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

        cls.q1 = Questions.objects.create(text="Tell us about yourself", category=category)
        cls.q2 = Questions.objects.create(text="Why this role?", category=category)

        candidate = User.objects.create_user("candidate", password="pw")
        application = Application.objects.create(
            user=candidate,
            pack=pack,
            answer_1="I want to learn on real projects.",
            answer_2="Organisation and communication.",
            answer_3="",
        )

        InterviewResult.objects.create(
            application=application,
            question=cls.q1,
            score=6,
            notes="Gave a confident, structured answer.",
            feedback="Strong communicator.",
        )
        InterviewResult.objects.create(application=application, question=cls.q2, score=2)

    def setUp(self):
        self.client.force_login(self.admin)

    def test_dashboard_shows_download_button(self):
        response = self.client.get(reverse("candidate_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Download PDF")
        self.assertContains(response, reverse("candidate_dashboard_pdf"))

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
