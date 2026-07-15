import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import (
    Application,
    ApplicationPack,
    Category,
    Indicator,
    IndicatorGroupScore,
    IndicatorScore,
    InterviewResult,
    Pack,
    PackGroup,
    Question,
)


class StartInterviewTest(TestCase):
    """Single-pack submission: the interview page, saving and re-saving."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "a@a.com", "pw")

        category = Category.objects.create(name="General")
        pack = Pack.objects.create(title="Pack 1", description="d", category=category)

        cls.question = Question.objects.create(text="Tell us about yourself", category=category)
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
        cls.ap = ApplicationPack.objects.create(application=cls.application, pack=pack, order=0)
        cls.ap = ApplicationPack.objects.create(application=cls.application, pack=pack)

    def setUp(self):
        self.client.force_login(self.admin)

    def interview_url(self):
        return reverse("start_interview", args=[self.application.application_id])

    def scores_payload(self, score):
        return {
            f"overall_score_{self.ap.id}_{self.question.id}": str(score),
            f"notes_{self.ap.id}_{self.question.id}": "Clear and confident.",
            f"feedback_{self.ap.id}_{self.question.id}": "Well done.",
            f"indicator_score_{self.indicator.id}": str(score),
            "group_score_Communication": str(score),
            "group_notes_Communication": "Generally strong.",
        }

    def test_interview_page_renders(self):
        response = self.client.get(self.interview_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.question.text)
        self.assertContains(response, "Communication")

    def test_submitting_scores_saves_results_and_average(self):
        response = self.client.post(self.interview_url(), {
            f"overall_score_{self.ap.id}_{self.question.id}": "5",
            f"notes_{self.ap.id}_{self.question.id}": "Clear and confident.",
            f"feedback_{self.ap.id}_{self.question.id}": "Well done.",
            f"indicator_score_{self.indicator.id}": "4",
            "group_score_Communication": "3",
            "group_notes_Communication": "Generally strong.",
        })
        response = self.client.post(self.interview_url(), self.scores_payload(5))
        self.assertRedirects(response, reverse("inbox"))

        result = InterviewResult.objects.get(application=self.application, question=self.question)
        self.assertEqual(result.score, 5)
        self.assertEqual(result.notes, "Clear and confident.")
        self.assertEqual(result.feedback, "Well done.")
        self.assertEqual(result.application_pack, self.ap)

        indicator_score = IndicatorScore.objects.get(
            application=self.application, indicator=self.indicator,
        )
        self.assertEqual(indicator_score.score, 5)

        group_score = IndicatorGroupScore.objects.get(
            application=self.application, group_name="Communication",
        )
        self.assertEqual(group_score.score, 5)
        self.assertEqual(group_score.notes, "Generally strong.")

        self.application.refresh_from_db()
        self.assertEqual(self.application.average_score, 5.0)

    def test_resubmitting_updates_existing_scores(self):
        self.client.post(self.interview_url(), {
            f"overall_score_{self.ap.id}_{self.question.id}": "2",
            f"indicator_score_{self.indicator.id}": "2",
            "group_score_Communication": "2",
        })
        self.client.post(self.interview_url(), {
            f"overall_score_{self.ap.id}_{self.question.id}": "6",
            f"indicator_score_{self.indicator.id}": "6",
            "group_score_Communication": "6",
        })
        self.client.post(self.interview_url(), self.scores_payload(2))
        self.client.post(self.interview_url(), self.scores_payload(6))

        self.assertEqual(InterviewResult.objects.count(), 1)
        self.assertEqual(IndicatorScore.objects.count(), 1)
        self.assertEqual(IndicatorGroupScore.objects.count(), 1)
        self.assertEqual(InterviewResult.objects.get().score, 6)
        self.assertEqual(IndicatorScore.objects.get().score, 6)
        self.assertEqual(IndicatorGroupScore.objects.get().score, 6)

    def test_autosave_saves_without_redirect(self):
        url = reverse("autosave_interview", args=[self.application.application_id])
        response = self.client.post(url, self.scores_payload(4))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertEqual(InterviewResult.objects.get().score, 4)


class GroupSubmissionFixture:
    """One candidate who applied to a two-pack group in one submission."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("admin", "a@a.com", "pw")

        maths = Category.objects.create(name="Maths")
        coding = Category.objects.create(name="Coding")
        cls.q_maths = Question.objects.create(text="Explain fractions", category=maths)
        cls.q_coding = Question.objects.create(text="Explain loops", category=coding)

        cls.pack_maths = Pack.objects.create(title="Maths Pack", description="d", category=maths)
        cls.pack_coding = Pack.objects.create(title="Coding Pack", description="d", category=coding)

        cls.group = PackGroup.objects.create(name="Grad Scheme")
        cls.group.packs.set([cls.pack_maths, cls.pack_coding])

        cls.candidate = User.objects.create_user("candidate", password="pw")
        cls.submission_id = uuid.uuid4()
        cls.row_maths = Application.objects.create(
            user=cls.candidate,
            group=cls.group,
            pack=cls.pack_maths,
            application_id=cls.submission_id,
            answer_1="m1", answer_2="m2", answer_3="m3",
        )
        cls.row_coding = Application.objects.create(
            user=cls.candidate,
            group=cls.group,
            pack=cls.pack_coding,
            application_id=cls.submission_id,
            answer_1="c1", answer_2="c2", answer_3="c3",
        )

    def setUp(self):
        self.client.force_login(self.admin)


class GroupInterviewTest(GroupSubmissionFixture, TestCase):
    def test_interview_covers_every_pack_in_the_submission(self):
        response = self.client.get(reverse("start_interview", args=[self.submission_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.q_maths.text)
        self.assertContains(response, self.q_coding.text)

        # Interview packs default to the submission's packs, on the primary row.
        self.assertEqual(
            list(self.row_maths.interview_packs.values_list("pack_id", flat=True)),
            [self.pack_maths.id, self.pack_coding.id],
        )
        self.assertFalse(self.row_coding.interview_packs.exists())

    def test_submitting_saves_results_per_pack(self):
        self.client.get(reverse("start_interview", args=[self.submission_id]))
        ap_maths, ap_coding = self.row_maths.interview_packs.order_by("order")

        response = self.client.post(reverse("start_interview", args=[self.submission_id]), {
            f"overall_score_{ap_maths.id}_{self.q_maths.id}": "4",
            f"notes_{ap_maths.id}_{self.q_maths.id}": "Solid on fundamentals.",
            f"feedback_{ap_maths.id}_{self.q_maths.id}": "Keep practising.",
            f"overall_score_{ap_coding.id}_{self.q_coding.id}": "6",
            f"notes_{ap_coding.id}_{self.q_coding.id}": "Excellent explanation.",
            f"feedback_{ap_coding.id}_{self.q_coding.id}": "Great depth.",
        })
        self.assertRedirects(response, reverse("inbox"))

        maths_result = InterviewResult.objects.get(question=self.q_maths)
        self.assertEqual(maths_result.application, self.row_maths)
        self.assertEqual(maths_result.application_pack, ap_maths)
        self.assertEqual(maths_result.score, 4)

        coding_result = InterviewResult.objects.get(question=self.q_coding)
        self.assertEqual(coding_result.application_pack, ap_coding)
        self.assertEqual(coding_result.notes, "Excellent explanation.")

        self.row_maths.refresh_from_db()
        self.assertEqual(self.row_maths.average_score, 5.0)


class ApproveApplicationTest(GroupSubmissionFixture, TestCase):
    def test_approve_accepts_all_rows_and_stores_pack_selection(self):
        response = self.client.post(
            reverse("approve_application", args=[self.submission_id]),
            {
                "interview_date": "2026-08-01T10:00",
                "interview_packs": [str(self.pack_coding.id), str(self.pack_maths.id)],
            },
        )
        self.assertRedirects(response, reverse("application_review"))

        self.row_maths.refresh_from_db()
        self.row_coding.refresh_from_db()
        self.assertEqual(self.row_maths.status, Application.STATUS_ACCEPTED)
        self.assertEqual(self.row_coding.status, Application.STATUS_ACCEPTED)
        self.assertIsNotNone(self.row_maths.interview_date)

        # Selection order is preserved on the primary row.
        chosen = list(
            self.row_maths.interview_packs.order_by("order").values_list("pack_id", flat=True)
        )
        self.assertEqual(chosen, [self.pack_coding.id, self.pack_maths.id])

    def test_deny_denies_all_rows(self):
        self.client.post(reverse("deny_application", args=[self.submission_id]))

        statuses = set(
            Application.objects
            .filter(application_id=self.submission_id)
            .values_list("status", flat=True)
        )
        self.assertEqual(statuses, {Application.STATUS_DENIED})

    def test_schedule_page_preselects_the_submissions_packs(self):
        response = self.client.get(reverse("approve_application", args=[self.submission_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.pack_maths.title)
        self.assertContains(response, self.pack_coding.title)


class ApplicantFormGroupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="General")
        cls.pack_1 = Pack.objects.create(
            title="Pack 1", description="d", category=category,
            pre_interview_question_1="Why?",
        )
        cls.pack_2 = Pack.objects.create(
            title="Pack 2", description="d", category=category,
            pre_interview_question_1="Why not?",
        )
        cls.group = PackGroup.objects.create(name="Grad Scheme")
        cls.group.packs.set([cls.pack_1, cls.pack_2])

        cls.applicant = User.objects.create_user("applicant", password="pw")

    def setUp(self):
        self.client.force_login(self.applicant)

    def step_url(self, step):
        return reverse("applicant_form_group", args=[self.group.id, step])

    def test_stepping_through_the_group_creates_one_submission(self):
        answers = {"answer_1": "a", "answer_2": "b", "answer_3": "c"}

        response = self.client.post(self.step_url(0), answers)
        self.assertRedirects(response, self.step_url(1))

        response = self.client.post(self.step_url(1), answers)
        self.assertRedirects(response, self.step_url(2), target_status_code=302)

        rows = Application.objects.filter(user=self.applicant).order_by("id")
        self.assertEqual(rows.count(), 2)
        self.assertEqual(len({row.application_id for row in rows}), 1)
        self.assertEqual([row.pack_id for row in rows], [self.pack_1.id, self.pack_2.id])
        self.assertTrue(all(row.group_id == self.group.id for row in rows))

    def test_skipping_ahead_without_a_session_restarts_the_flow(self):
        response = self.client.get(self.step_url(1))
        self.assertRedirects(response, self.step_url(0))


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
