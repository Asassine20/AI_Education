# ai_app/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import CourseMaterial
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ['file', 'display_name', 'category', 'visible_to_students']