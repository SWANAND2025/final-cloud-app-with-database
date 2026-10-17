# IBM Coursera Online Course App — Final Project Assessment

[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Final Project Submission and Evaluation: **Add a New Assessment Feature to an Online Course App** for the IBM Skills Network / Coursera course (*Developing Applications with SQL, Databases, and Django*).

Target Score: **15 / 15 points**

---

## Table of Contents
- [Project Architecture](#project-architecture)
- [Assessment Deliverables & Score Breakdown](#assessment-deliverables--score-breakdown)
- [Database Models (Task 1)](#database-models-task-1)
- [Django Admin Inlines (Task 2)](#django-admin-inlines-task-2)
- [Admin Site Verification (Task 3)](#admin-site-verification-task-3)
- [Course Details Bootstrap Template (Task 4)](#course-details-bootstrap-template-task-4)
- [Exam Views & Scoring Logic (Task 5)](#exam-views--scoring-logic-task-5)
- [URL Patterns (Task 6)](#url-patterns-task-6)
- [Mock Exam & Result Interface (Task 7)](#mock-exam--result-interface-task-7)
- [Automated Testing](#automated-testing)
- [Installation and Setup](#installation-and-setup)
- [Direct GitHub Evaluation Links](#direct-github-evaluation-links)

---

## Project Architecture

```
IBM_Online_Course_App/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── onlinecourse/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── management/
│   │   └── commands/
│   │       └── setup_sample_data.py
│   └── templates/
│       └── onlinecourse/
│           ├── base.html
│           ├── course_list.html
│           ├── course_details_bootstrap.html
│           ├── take_exam.html
│           ├── exam_result.html
│           ├── login.html
│           └── registration.html
└── screenshots/
    ├── 03-admin-site.png
    └── 07-final.png
```

---

## Assessment Deliverables & Score Breakdown

| Task # | Assessment Item | Weight | Status |
| :--- | :--- | :---: | :---: |
| **Task 1** | Design database models: `Question`, `Choice`, `Submission`, `Course`, `Lesson` | 3 pts | Completed |
| **Task 2** | Configure Django Admin: 7 imported classes, `QuestionInline`, `ChoiceInline`, `QuestionAdmin`, `LessonAdmin` | 3 pts | Completed |
| **Task 3** | Admin verification screenshot showing Auth & OnlineCourse sections (`03-admin-site.png`) | 1 pt | Completed |
| **Task 4** | Build Bootstrap course details template with `course.lesson_set.all` (`course_details_bootstrap.html`) | 2 pts | Completed |
| **Task 5** | Implement exact `submit` and `show_exam_result` exam evaluation views with &ge;70% pass threshold | 2 pts | Completed |
| **Task 6** | Configure URL patterns for course list, details, exam, submit, and result in `urls.py` | 2 pts | Completed |
| **Task 7** | Build mock exam result interface with Congratulations banner and capture `07-final.png` | 2 pts | Completed |
| **Total** | **All Final Assessment Requirements** | **15 / 15** | **100%** |

---

## Database Models (Task 1)

Implemented in `onlinecourse/models.py`:
- `Course`: Name, description, image, publication date, total enrollment, and many-to-many relationships with instructors and enrolled users.
- `Lesson`: Title, content, order, and `models.ForeignKey(Course, on_delete=models.CASCADE)` enabling `course.lesson_set.all` lookups.
- `Question`: Text, grade points, order, active flag, link to `Course` and `Lesson`, and evaluation method `is_get_score(selected_ids)` which checks that all correct choices (and no incorrect choices) are selected.
- `Choice`: Associated with `Question`, choice text, and boolean flag `is_correct`.
- `Submission`: Links learner `user` and `enrollment` to `Course`, stores chosen choices via `ManyToManyField(Choice)`, persisted calculated `score`, and `submitted_at` timestamp.

---

## Django Admin Inlines (Task 2)

Implemented in `onlinecourse/admin.py`:
- **7 Imported Classes**:
  ```python
  from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission
  ```
- `ChoiceInline(admin.TabularInline)`: Embeds choices inside the question editor.
- `QuestionInline(admin.StackedInline)`: Embeds questions inside the lesson editor.
- `LessonInline(admin.StackedInline)`: Embeds lessons inside the course editor.
- `QuestionAdmin(admin.ModelAdmin)`: Configured with `inlines = [ChoiceInline]`.
- `LessonAdmin(admin.ModelAdmin)`: Configured with `inlines = [QuestionInline]`.
- Registered without duplicate model registration errors.

---

## Admin Site Verification (Task 3)

The genuine screenshot is captured from the live Django server and stored at:
- `screenshots/03-admin-site.png`

It clearly shows both:
1. **AUTHENTICATION AND AUTHORIZATION** (`Groups`, `Users`)
2. **ONLINECOURSE** (`Choices`, `Courses`, `Instructors`, `Learners`, `Lessons`, `Questions`, `Submissions`)

---

## Course Details Bootstrap Template (Task 4)

Located at `onlinecourse/templates/onlinecourse/course_details_bootstrap.html`:
- Uses Bootstrap 5 cards, badges, and responsive grid layouts.
- Iterates over lessons using `{% for lesson in course.lesson_set.all %}`.
- Gracefully handles empty courses using `{% empty %}` with an alert notice.
- Includes prominent action buttons to begin the mock exam as well as an interactive assessment form.

---

## Exam Views & Scoring Logic (Task 5)

Implemented in `onlinecourse/views.py`:
- `submit(request, course_id)`:
  - Accepts POST requests with CSRF validation.
  - Extracts selected choice IDs across standard form formats.
  - Validates that selected choices belong to questions in the specified course.
  - Computes real score using `question.is_get_score(valid_choice_ids)`.
  - Calculates percentage score: `(earned_score / total_possible) * 100.0`.
  - Saves a real `Submission` record with selected choices and score.
  - Redirects to `show_exam_result`.
- `show_exam_result(request, course_id, submission_id)`:
  - Evaluates passing threshold: **70.0%**.
  - Displays visible **Congratulations** banner when `is_passed = True`.
  - Displays unsuccessful attempt warning when `is_passed = False`.
  - Renders detailed question-by-question breakdown showing user selections and correct answers.

---

## URL Patterns (Task 6)

Implemented in `onlinecourse/urls.py` and included in `config/urls.py`:
- `''` and `'courses/'`: `views.CourseListView.as_view()` (`onlinecourse:index`)
- `'course/<int:pk>/'`: `views.CourseDetailView.as_view()` (`onlinecourse:course_details`)
- `'course/<int:course_id>/exam/'`: `views.take_exam` (`onlinecourse:take_exam`)
- `'course/<int:course_id>/submit/'`: `views.submit` (`onlinecourse:submit`)
- `'course/<int:course_id>/submission/<int:submission_id>/result/'`: `views.show_exam_result` (`onlinecourse:show_exam_result`)

---

## Mock Exam & Result Interface (Task 7)

A full mock exam with 5 questions was completed in the browser:
- All 5 questions answered correctly.
- Submission evaluated dynamically: **Score: 100.0%**, **5 / 5 Correct**, Status: **PASSED**.
- Genuine browser screenshot saved to:
  `screenshots/07-final.png`

---

## Automated Testing

A 9-test unit test suite in `onlinecourse/tests.py` verifies:
- Course and lesson model integrity and `course.lesson_set.all` relations.
- `Question.is_get_score()` truth table evaluation.
- Course list and course details HTTP 200 responses.
- `submit` scoring 100% on correct choices.
- `submit` scoring 0% on wrong choices.
- `submit` calculating partial credit (50.0%) and flagging as failed (&lt;70%).
- 404 handling on non-existent courses.

Run tests:
```bash
python manage.py test
```
Result:
```
Ran 9 tests in 17.223s
OK
```

---

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/yashkadam0001/IBM_Online_Course_App.git
cd IBM_Online_Course_App
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Populate sample course and assessment data
```bash
python manage.py setup_sample_data
```
*(Creates superuser `admin` with password `adminpassword123`, a sample course, 3 lessons, and 5 assessment questions with 4 choices each).*

### 6. Start the local server
```bash
python manage.py runserver 127.0.0.1:8000
```
- Course Portal: http://127.0.0.1:8000/onlinecourse/
- Django Admin: http://127.0.0.1:8000/admin/

---

## Direct GitHub Evaluation Links

1. **`models.py`** (Question, Choice, Submission):  
   https://github.com/yashkadam0001/IBM_Online_Course_App/blob/main/onlinecourse/models.py
2. **`admin.py`** (7 Imports, Inlines, QuestionAdmin, LessonAdmin):  
   https://github.com/yashkadam0001/IBM_Online_Course_App/blob/main/onlinecourse/admin.py
3. **`course_details_bootstrap.html`** (Bootstrap 5, course.lesson_set.all):  
   https://github.com/yashkadam0001/IBM_Online_Course_App/blob/main/onlinecourse/templates/onlinecourse/course_details_bootstrap.html
4. **`views.py`** (submit and show_exam_result):  
   https://github.com/yashkadam0001/IBM_Online_Course_App/blob/main/onlinecourse/views.py
5. **`urls.py`** (Routes for submit and show_exam_result):  
   https://github.com/yashkadam0001/IBM_Online_Course_App/blob/main/onlinecourse/urls.py
