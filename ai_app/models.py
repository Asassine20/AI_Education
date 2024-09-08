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

class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)  # Unique university code

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    room_name = models.CharField(max_length=255)
    room_code = models.CharField(max_length=50, unique=True)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_teaching')

    def __str__(self):
        return self.room_name
    
class SchoolUserProfile(models.Model):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    classes = models.ManyToManyField(ClassRoom, related_name='students', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"