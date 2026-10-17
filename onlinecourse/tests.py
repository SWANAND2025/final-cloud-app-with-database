from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from onlinecourse.models import Course, Lesson, Question, Choice, Submission


class OnlineCourseModelAndAssessmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testlearner',
            password='testpassword123'
        )

        # Create Course
        self.course = Course.objects.create(
            name="Test Django Course",
            description="Testing course description and lesson rendering.",
            total_enrollment=50
        )

        # Create Lessons
        self.lesson1 = Lesson.objects.create(
            title="Lesson 1: Foundations",
            course=self.course,
            order=1,
            content="Foundations content text."
        )
        self.lesson2 = Lesson.objects.create(
            title="Lesson 2: Advanced Topics",
            course=self.course,
            order=2,
            content="Advanced topics content text."
        )

        # Create Questions & Choices
        # Question 1: 1 point
        self.q1 = Question.objects.create(
            course=self.course,
            lesson=self.lesson1,
            question_text="Is Django a Python web framework?",
            grade=1,
            order=1,
            is_active=True
        )
        self.c1_correct = Choice.objects.create(
            question=self.q1,
            choice_text="Yes, Django is a high-level Python framework.",
            is_correct=True
        )
        self.c1_wrong = Choice.objects.create(
            question=self.q1,
            choice_text="No, it is a Java runtime engine.",
            is_correct=False
        )

        # Question 2: 1 point
        self.q2 = Question.objects.create(
            course=self.course,
            lesson=self.lesson2,
            question_text="Which file defines database models?",
            grade=1,
            order=2,
            is_active=True
        )
        self.c2_correct = Choice.objects.create(
            question=self.q2,
            choice_text="models.py",
            is_correct=True
        )
        self.c2_wrong = Choice.objects.create(
            question=self.q2,
            choice_text="views.py",
            is_correct=False
        )

    def test_course_and_lesson_creation(self):
        """Verify course and lesson models and reverse relation lesson_set."""
        self.assertEqual(self.course.name, "Test Django Course")
        self.assertEqual(self.course.lesson_set.count(), 2)
        lessons = list(self.course.lesson_set.all())
        self.assertIn(self.lesson1, lessons)
        self.assertIn(self.lesson2, lessons)

    def test_question_is_get_score_evaluation(self):
        """Verify is_get_score returns True only when correct answers match."""
        # Correct choice selected
        self.assertTrue(self.q1.is_get_score([self.c1_correct.id]))
        # Wrong choice selected
        self.assertFalse(self.q1.is_get_score([self.c1_wrong.id]))
        # Both correct and wrong choice selected
        self.assertFalse(self.q1.is_get_score([self.c1_correct.id, self.c1_wrong.id]))
        # No choices selected
        self.assertFalse(self.q1.is_get_score([]))

    def test_course_list_view(self):
        """Verify course listing page renders HTTP 200 and displays course."""
        url = reverse('onlinecourse:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Django Course")
        self.assertContains(response, "Explore Courses")

    def test_course_details_view(self):
        """Verify course details page renders HTTP 200 and displays lessons using course.lesson_set.all."""
        url = reverse('onlinecourse:course_details', kwargs={'pk': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Django Course")
        self.assertContains(response, "Lesson 1: Foundations")
        self.assertContains(response, "Lesson 2: Advanced Topics")
        self.assertContains(response, "Course Curriculum &amp; Lessons")

    def test_take_exam_view(self):
        """Verify dedicated mock exam view loads questions."""
        url = reverse('onlinecourse:take_exam', kwargs={'course_id': self.course.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Is Django a Python web framework?")
        self.assertContains(response, "Which file defines database models?")

    def test_submit_exam_all_correct_passes(self):
        """Verify submit view processes 100% correct answers, creates Submission, and passes."""
        url = reverse('onlinecourse:submit', kwargs={'course_id': self.course.id})
        post_data = {
            f'choice_{self.q1.id}': self.c1_correct.id,
            f'choice_{self.q2.id}': self.c2_correct.id,
        }
        response = self.client.post(url, post_data)
        
        # Should redirect to show_exam_result
        self.assertEqual(response.status_code, 302)
        
        # Verify Submission in database
        submission = Submission.objects.filter(course=self.course).latest('id')
        self.assertEqual(submission.score, 100.0)
        self.assertEqual(submission.choices.count(), 2)

        # Follow redirect to result page
        result_response = self.client.get(response.url)
        self.assertEqual(result_response.status_code, 200)
        self.assertContains(result_response, "Congratulations! You Passed the Exam!")
        self.assertContains(result_response, "100.0%")
        self.assertContains(result_response, "2 / 2")
        self.assertContains(result_response, "PASSED")

    def test_submit_exam_incorrect_fails(self):
        """Verify submit view processes incorrect answers with score < 70% and shows unsuccessful message."""
        url = reverse('onlinecourse:submit', kwargs={'course_id': self.course.id})
        post_data = {
            f'choice_{self.q1.id}': self.c1_wrong.id,
            f'choice_{self.q2.id}': self.c2_wrong.id,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        submission = Submission.objects.filter(course=self.course).latest('id')
        self.assertEqual(submission.score, 0.0)

        result_response = self.client.get(response.url)
        self.assertEqual(result_response.status_code, 200)
        self.assertNotContains(result_response, "Congratulations! You Passed the Exam!")
        self.assertContains(result_response, "Exam Attempt Not Passed")
        self.assertContains(result_response, "0.0%")
        self.assertContains(result_response, "FAILED")

    def test_submit_exam_partial_score(self):
        """Verify 1 out of 2 correct questions calculates 50.0% and evaluates as failed (<70%)."""
        url = reverse('onlinecourse:submit', kwargs={'course_id': self.course.id})
        post_data = {
            f'choice_{self.q1.id}': self.c1_correct.id,
            f'choice_{self.q2.id}': self.c2_wrong.id,
        }
        response = self.client.post(url, post_data)
        self.assertEqual(response.status_code, 302)

        submission = Submission.objects.filter(course=self.course).latest('id')
        self.assertEqual(submission.score, 50.0)

        result_response = self.client.get(response.url)
        self.assertEqual(result_response.status_code, 200)
        self.assertContains(result_response, "50.0%")
        self.assertContains(result_response, "1 / 2")

    def test_submit_invalid_course(self):
        """Submitting to a non-existent course returns 404."""
        url = reverse('onlinecourse:submit', kwargs={'course_id': 99999})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 404)
