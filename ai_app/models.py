from django.db import models
from django.contrib.auth.models import User
import jsonfield
from django_quill.fields import QuillField 

class CourseMaterial(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
    material = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    classroom = models.ForeignKey('ClassRoom', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    category=models.CharField(max_length=255, null=True, blank=True)
    visible_to_students = models.BooleanField(default=False)  
    is_syllabus = models.BooleanField(default=False)  # New column to handle syllabus marking

    def __str__(self):
        return self.display_name if self.display_name else self.file.name

class University(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)  # Unique university code
    logo = models.ImageField(upload_to='university_logos/')
    
    def __str__(self):
        return self.name

class ClassRoom(models.Model):
    room_name = models.CharField(max_length=255)
    room_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True) 
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes_teaching')
    students = models.ManyToManyField(User, related_name='enrolled_classrooms', blank=True)  
    room_number = models.CharField(max_length=10)
    class_times = jsonfield.JSONField(blank=True, null=True)

    def __str__(self):
        return self.room_name

class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)

class SchoolUserProfile(models.Model):
    STUDENT = 'student'
    TEACHER = 'teacher'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (TEACHER, 'Teacher'),
        (ADMIN, 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    classes = models.ManyToManyField(ClassRoom, related_name='school_profiles', blank=True)  # Updated related_name to avoid conflict

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='assignments')

    def __str__(self):
        return self.title
    
class Messages(models.Model):
    title = models.CharField(max_length=255)
    text = QuillField()

    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='messages')
    
    def __str__(self):
        return self.title