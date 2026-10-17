from django.urls import path
from . import views

app_name = 'onlinecourse'

urlpatterns = [
    # Course listing routes
    path('', views.CourseListView.as_view(), name='index'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),

    # Course details routes
    path('course/<int:pk>/', views.CourseDetailView.as_view(), name='course_details'),
    path('<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),

    # Taking the mock exam
    path('course/<int:course_id>/exam/', views.take_exam, name='take_exam'),
    path('<int:course_id>/exam/', views.take_exam, name='exam'),

    # Assessment submit routes
    path('course/<int:course_id>/submit/', views.submit, name='submit'),
    path('<int:course_id>/submit/', views.submit, name='submit_alt'),

    # Assessment show_exam_result routes
    path('course/<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='show_exam_result'),
    path('<int:course_id>/submission/<int:submission_id>/result/', views.show_exam_result, name='show_exam_result_alt'),

    # User authentication & enrollment
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),
    path('registration/', views.registration_request, name='registration'),
    path('enroll/<int:course_id>/', views.enroll, name='enroll'),
]
