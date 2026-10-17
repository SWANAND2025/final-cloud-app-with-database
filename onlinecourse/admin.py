from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'pub_date', 'total_enrollment')
    list_filter = ['pub_date']
    search_fields = ['name', 'description']


class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    inlines = [QuestionInline]
    list_filter = ['course']
    search_fields = ['title', 'content']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ['question_text', 'course', 'lesson', 'grade', 'order', 'is_active']
    list_filter = ['course', 'lesson', 'is_active']
    search_fields = ['question_text']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question']
    search_fields = ['choice_text']


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course', 'score', 'submitted_at']
    list_filter = ['course', 'submitted_at']
    filter_horizontal = ('choices',)


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)
