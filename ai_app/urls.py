from django.urls import path

from .views.auth_views import login_view, logout_view, signup_view, school_signup_view, individual_signup_view
from .views.dashboard_views import teacher_dashboard, student_dashboard, individual_dashboard
from .views.other_views import home, landing_page, contact_view
from .views.question_views import ask_question, upload_materials, view_questions
urlpatterns = [
    path("", landing_page, name="landing_page"),  # Landing page route
    path("home/", home, name="home"),  # Home page route after login/signup
    path("ask/", ask_question, name="ask_question"),
    path('upload-materials/', upload_materials, name='upload_materials'),
    path('view-questions/', view_questions, name='view_questions'),
    path('signup/', signup_view, name='signup'),
    path('school-signup/', school_signup_view, name='school_signup'),  # Added school-specific sign-up route
    path('individual-signup/', individual_signup_view, name='individual_signup'),  # Added individual-specific sign-up route
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_view, name='contact'),
    path('student-dashboard/', student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('individual-dashboard/', individual_dashboard, name='individual_dashboard'),  # Individual user dashboard
]
