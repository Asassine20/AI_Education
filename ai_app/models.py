from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class CourseMaterial(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    material = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
