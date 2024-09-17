from django.urls import path

from .views.auth_views import login_view, logout_view, signup_view, school_signup_view
from .views.dashboard_views import teacher_dashboard, student_dashboard, add_class, course_page, students_enrolled, student_questions, students_in_class, assignments_in_class, grades_in_class, syllabus_in_class, subjects_in_class, messages_list
from .views.other_views import home, landing_page, contact_view
from .views.question_views import ask_question, upload_materials, view_questions
from .views.file_views import file_preview_view, file_download_view, file_list_view, file_upload_view, file_edit_view

urlpatterns = [
    path("", landing_page, name="landing_page"),  # Landing page route
    path("home/", home, name="home"),  # Home page route after login/signup
    path("ask/", ask_question, name="ask_question"),
    path('view-questions/', view_questions, name='view_questions'),
    path('signup/', signup_view, name='signup'),
    path('school-signup/', school_signup_view, name='school_signup'),  # Added school-specific sign-up route
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_view, name='contact'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher-dashboard/add-class/', add_class, name='add_class'),
    path('teacher-dashboard/course/<str:room_code>/', course_page, name='course_page'),
    path('teacher-dashboard/course/<str:room_code>/students-enrolled/', students_enrolled, name='students_enrolled'),
    path('teacher-dashboard/course/<str:room_code>/student-questions/', student_questions, name='student_questions'),
    path('teacher-dashboard/course/<str:room_code>/messages/', messages_list, name='messages_list'),
    path('teacher-dashboard/course/<str:room_code>/upload-materials/', upload_materials, name='upload_materials'),
    path('student-dashboard/course/<str:room_code>/students/', students_in_class, name='students_in_class'),
    path('student-dashboard/course/<str:room_code>/assignments/', assignments_in_class, name='assignments_in_class'),
    path('student-dashboard/course/<str:room_code>/grades/', grades_in_class, name='grades_in_class'),
    path('student-dashboard/course/<str:room_code>/syllabus/', syllabus_in_class, name='syllabus_in_class'),
    path('student-dashboard/course/<str:room_code>/subjects/', subjects_in_class, name='subjects_in_class'),
    path('teacher-dashboard/course/<str:room_code>/upload/', file_upload_view, name='file_upload'),
    path('teacher-dashboard/course/<str:room_code>/files/', file_list_view, name='file_list'),
    path('teacher-dashboard/course/<str:room_code>/edit/<int:file_id>/', file_edit_view, name='file_edit'),
    path('teacher-dashboard/course/<str:room_code>/download/<int:file_id>/', file_download_view, name='file_download'),
    path('teacher-dashboard/course/<str:room_code>/<str:display_name>/', file_preview_view, name='file_preview'),
    ]
