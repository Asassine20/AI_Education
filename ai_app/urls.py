from .views import ask_question, upload_materials, view_questions, signup_view, login_view, logout_view, home
from django.urls import path

urlpatterns = [
    path("", home, name="home"),  # Home page
    path("ask/", ask_question, name="ask_question"),
    path('upload-materials/', upload_materials, name='upload_materials'),
    path('view-questions/', view_questions, name='view_questions'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
