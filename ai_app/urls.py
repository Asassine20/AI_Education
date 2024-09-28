from django.urls import path
from .views import *

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
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/add-class/', add_class, name='add_class'),
    path('dashboard/course/<str:room_code>/', course_page, name='course_page'),
    path('dashboard/course/<str:room_code>//download/<int:file_id>/', download_syllabus, name='download_syllabus'),
    path('dashboard/course/<str:room_code>/preview-syllabus/<int:file_id>/', preview_syllabus, name='preview_syllabus'),
    path('dashboard/course/<str:room_code>/students-enrolled/', students_enrolled, name='students_enrolled'),
    path('dashboard/course/<str:room_code>/student-questions/', student_questions, name='student_questions'),
    path('dashboard/course/<str:room_code>/messages/', messages_list, name='messages_list'),
    path('dashboard/course/<str:room_code>/assignments_list/', assignments_list, name='assignments_list'),
    path('dashboard/course/<str:room_code>/assignment/<int:assignment_id>/', assignment_page, name='assignment_page'),
    path('dashboard/course/<str:room_code>/assignments/create-assignment/', create_assignment, name='create_assignment'),
    path('dashboard/course/<str:room_code>/messages/create-message/', create_message, name='create_message'),
    path('dashboard/course/<str:room_code>/messages/<int:message_id>/delete', delete_message, name='delete_message'),
    path('dashboard/course/<str:room_code>/upload-materials/', upload_materials, name='upload_materials'),
    path('dashboard/course/<str:room_code>/upload/', file_upload_view, name='file_upload'),
    path('dashboard/course/<str:room_code>/files/', file_list_view, name='file_list'),
    path('dashboard/course/<str:room_code>/edit/<int:file_id>/', file_edit_view, name='file_edit'),
    path('dashboard/course/<str:room_code>/download/<int:file_id>/', file_download_view, name='file_download'),
    path('dashboard/course/<str:room_code>/<str:display_name>/', file_preview_view, name='file_preview'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/image-upload/<str:code>/', university_logo_upload_view, name='university_logo_upload'),
    path('admin-dashboard/display-logo/<str:code>/', display_logo, name='display_logo'),
    path('dashboard/profile-image-upload/', profile_image_upload_view, name='profile_image_upload')
    ]

