import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from onlinecourse.models import Course, Lesson, Question, Choice, Instructor, Learner


class Command(BaseCommand):
    help = 'Populates the database with realistic course, lesson, and assessment data'

    def handle(self, *args, **options):
        self.stdout.write("Setting up sample data for IBM Online Course App...")

        # 1. Ensure Superuser exists
        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword123')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

        if not User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS(f"Created superuser '{admin_username}'."))
        else:
            admin_user = User.objects.get(username=admin_username)
            admin_user.set_password(admin_password)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Updated superuser '{admin_username}'."))

        # 2. Create Instructor
        instructor, _ = Instructor.objects.get_or_create(
            user=admin_user,
            defaults={'full_time': True, 'total_learners': 1500}
        )

        # 3. Create Learner profile
        Learner.objects.get_or_create(
            user=admin_user,
            defaults={'occupation': 'developer', 'social_link': 'https://github.com/ibm'}
        )

        # 4. Create Course
        course, created = Course.objects.get_or_create(
            name="Cloud Application Development with Django and SQL",
            defaults={
                'description': (
                    "Gain comprehensive expertise in backend web application development using Python, "
                    "Django, SQLite, and relational database patterns. Master models, views, templates, "
                    "inline admin customization, and robust exam submission architectures."
                ),
                'pub_date': timezone.now().date(),
                'total_enrollment': 284,
            }
        )
        course.instructors.add(instructor)
        self.stdout.write(self.style.SUCCESS(f"Course ready: '{course.name}'"))

        # 5. Create Lessons
        lesson1, _ = Lesson.objects.get_or_create(
            title="Lesson 1: Introduction to Django Framework and Architecture",
            course=course,
            defaults={
                'order': 1,
                'content': (
                    "Django is a high-level Python web framework designed to encourage rapid development and clean, "
                    "pragmatic design. It follows the Model-View-Template (MVT) architectural pattern. In this module, "
                    "learners discover how URL dispatchers route requests to view functions, how Django handles HTTP request "
                    "cycles, and how to organize modular applications using manage.py."
                )
            }
        )

        lesson2, _ = Lesson.objects.get_or_create(
            title="Lesson 2: Django Models, ORM, and Database Migrations",
            course=course,
            defaults={
                'order': 2,
                'content': (
                    "Django's Object-Relational Mapper (ORM) allows developers to define database schemas in Python code. "
                    "Through models.Model subclasses, developers declare fields, foreign keys, and many-to-many relationships. "
                    "Running makemigrations inspects model declarations and drafts migration operations, while migrate executes "
                    "those schema changes against the underlying SQLite or PostgreSQL database."
                )
            }
        )

        lesson3, _ = Lesson.objects.get_or_create(
            title="Lesson 3: Django Views, Bootstrap 5 Templates, and Assessment Submission",
            course=course,
            defaults={
                'order': 3,
                'content': (
                    "Connecting data to user interfaces requires robust views and accessible presentation templates. "
                    "In this lesson, we study how to render course details with Bootstrap 5 cards and accordions, construct "
                    "dynamic assessment forms, accept POST data with CSRF validation, evaluate question scores accurately, "
                    "and persist student submissions."
                )
            }
        )
        self.stdout.write(self.style.SUCCESS("3 Lessons created."))

        # 6. Create 5 Realistic Assessment Questions and Choices
        questions_data = [
            {
                'text': "What architectural design pattern does the Django web framework follow?",
                'grade': 1,
                'order': 1,
                'lesson': lesson1,
                'choices': [
                    ("Model-View-Template (MVT)", True),
                    ("Model-View-Controller (MVC) exclusively", False),
                    ("Single-Page Reactive Component Architecture", False),
                    ("Pipe-and-Filter Microkernel Pattern", False),
                ]
            },
            {
                'text': "Which Django management command generates new schema migration files after modifying models.py?",
                'grade': 1,
                'order': 2,
                'lesson': lesson2,
                'choices': [
                    ("python manage.py makemigrations", True),
                    ("python manage.py migrate", False),
                    ("python manage.py sqlmigrate", False),
                    ("python manage.py syncdb", False),
                ]
            },
            {
                'text': "In Django admin, which class configuration allows managing child Choice records directly on a Question change page?",
                'grade': 1,
                'order': 3,
                'lesson': lesson2,
                'choices': [
                    ("admin.TabularInline or admin.StackedInline", True),
                    ("admin.NestedModelAdmin", False),
                    ("admin.RelatedSetController", False),
                    ("admin.ChildModelFormView", False),
                ]
            },
            {
                'text': "How do you iterate over all lessons associated with a course in a Django template when using default related names?",
                'grade': 1,
                'order': 4,
                'lesson': lesson3,
                'choices': [
                    ("{% for lesson in course.lesson_set.all %}", True),
                    ("{% for lesson in course.get_all_lessons %}", False),
                    ("{% for lesson in course.lessons_list %}", False),
                    ("{% for lesson in Course.objects.all %}", False),
                ]
            },
            {
                'text': "Which Django template tag must be included in an HTML POST form to protect against Cross-Site Request Forgery?",
                'grade': 1,
                'order': 5,
                'lesson': lesson3,
                'choices': [
                    ("{% csrf_token %}", True),
                    ("{% verify_authenticity %}", False),
                    ("{% secure_form %}", False),
                    ("{% anti_forgery_key %}", False),
                ]
            },
        ]

        # Clear existing questions for clean setup
        Question.objects.filter(course=course).delete()

        for q_item in questions_data:
            question = Question.objects.create(
                course=course,
                lesson=q_item['lesson'],
                question_text=q_item['text'],
                grade=q_item['grade'],
                order=q_item['order'],
                is_active=True
            )
            question.courses.add(course)

            for choice_text, is_corr in q_item['choices']:
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=is_corr
                )

        self.stdout.write(self.style.SUCCESS(f"Successfully configured 5 questions with 4 choices each."))
        self.stdout.write(self.style.SUCCESS("Sample data setup completed successfully!"))
