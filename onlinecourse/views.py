from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from .models import Course, Lesson, Question, Choice, Submission, Enrollment


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-pub_date')[:20]


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        # Retrieve all active questions associated with this course or its lessons
        questions = Question.objects.filter(course=course, is_active=True).distinct()
        if not questions.exists():
            questions = Question.objects.filter(lesson__course=course, is_active=True).distinct()
        context['questions'] = questions
        return context


def take_exam(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = Question.objects.filter(course=course, is_active=True).distinct()
    if not questions.exists():
        questions = Question.objects.filter(lesson__course=course, is_active=True).distinct()
    
    context = {
        'course': course,
        'questions': questions,
    }
    return render(request, 'onlinecourse/take_exam.html', context)


def submit(request, course_id):
    if request.method != 'POST':
        return redirect('onlinecourse:course_details', pk=course_id)

    course = get_object_or_404(Course, pk=course_id)
    
    # Retrieve all valid questions for this course
    questions = Question.objects.filter(course=course, is_active=True).distinct()
    if not questions.exists():
        questions = Question.objects.filter(lesson__course=course, is_active=True).distinct()

    if not questions.exists():
        messages.error(request, "This course currently has no exam questions available.")
        return redirect('onlinecourse:course_details', pk=course.id)

    # Extract submitted choice IDs from the POST data
    selected_choice_ids = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            # Case 1: radio button name="choice_<question_id>" with value="<choice_id>"
            try:
                selected_choice_ids.append(int(value))
            except (ValueError, TypeError):
                # Case 2: checkbox name="choice_<choice_id>" with value="on" or "true"
                parts = key.split('_')
                if len(parts) > 1:
                    try:
                        selected_choice_ids.append(int(parts[1]))
                    except (ValueError, TypeError):
                        pass

    # Support standard getlist for 'choice' or 'choices'
    for cid in request.POST.getlist('choice') + request.POST.getlist('choices'):
        try:
            selected_choice_ids.append(int(cid))
        except (ValueError, TypeError):
            pass

    selected_choice_ids = list(set(selected_choice_ids))

    # Verify that each selected choice belongs to the course's questions
    valid_choices = Choice.objects.filter(
        id__in=selected_choice_ids,
        question__in=questions
    )
    valid_choice_ids = set(valid_choices.values_list('id', flat=True))

    # Calculate real score based on question evaluation
    total_possible_score = sum(q.grade for q in questions)
    earned_score = 0

    for question in questions:
        if question.is_get_score(valid_choice_ids):
            earned_score += question.grade

    # Compute percentage score (0.0 to 100.0)
    if total_possible_score > 0:
        score_percentage = round((earned_score / total_possible_score) * 100.0, 2)
    else:
        score_percentage = 0.0

    # Create submission record
    user = request.user if request.user.is_authenticated else None
    enrollment = Enrollment.objects.filter(user=user, course=course).first() if user else None

    submission = Submission.objects.create(
        user=user,
        enrollment=enrollment,
        course=course,
        score=score_percentage
    )
    submission.choices.set(valid_choices)

    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id, course=course)

    # Retrieve all questions evaluated for this exam
    questions = Question.objects.filter(course=course, is_active=True).distinct()
    if not questions.exists():
        questions = Question.objects.filter(lesson__course=course, is_active=True).distinct()

    selected_choices = submission.choices.all()
    selected_choice_ids = set(selected_choices.values_list('id', flat=True))

    total_questions = questions.count()
    correct_count = 0
    questions_results = []

    for question in questions:
        is_correct = question.is_get_score(selected_choice_ids)
        if is_correct:
            correct_count += 1

        choices_data = []
        for choice in question.choice_set.all():
            is_selected = choice.id in selected_choice_ids
            choices_data.append({
                'choice': choice,
                'is_selected': is_selected,
                'is_correct': choice.is_correct,
            })

        questions_results.append({
            'question': question,
            'is_correct': is_correct,
            'choices': choices_data,
        })

    passing_threshold = 70.0
    is_passed = submission.score >= passing_threshold

    context = {
        'course': course,
        'submission': submission,
        'grade': submission.score,
        'score': submission.score,
        'score_percentage': submission.score,
        'total_questions': total_questions,
        'correct_count': correct_count,
        'is_passed': is_passed,
        'passing_threshold': passing_threshold,
        'questions_results': questions_results,
        'selected_ids': selected_choice_ids,
    }
    return render(request, 'onlinecourse/exam_result.html', context)


# User Authentication and Enrollment Views
def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('onlinecourse:index')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'onlinecourse/login.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('onlinecourse:index')


def registration_request(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('onlinecourse:index')
        messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = UserCreationForm()
    return render(request, 'onlinecourse/registration.html', {'form': form})


def enroll(request, course_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in before enrolling in a course.")
        return redirect('onlinecourse:login')
    
    course = get_object_or_404(Course, pk=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)
    if created:
        course.total_enrollment += 1
        course.save()
        messages.success(request, f"Successfully enrolled in {course.name}!")
    else:
        messages.info(request, f"You are already enrolled in {course.name}.")
    return redirect('onlinecourse:course_details', pk=course.id)
