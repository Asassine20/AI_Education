from django.db import models
from django.contrib.auth.models import User
from django_quill.fields import QuillField 

class CourseMaterial(models.Model):
    professor = models.ForeignKey(User, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)
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
    primary_color = models.CharField(max_length=7, default='#00274C')
    secondary_color = models.CharField(max_length=7, default='#FFCB05')
    font_family = models.CharField(max_length=255, blank=True, null=True)
    
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
    class_times = models.JSONField(blank=True, null=True)

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
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    classes = models.ManyToManyField(ClassRoom, related_name='school_profiles', blank=True)  # Updated related_name to avoid conflict

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Category(models.Model):
    points = models.CharField(max_length=20)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='classrooms')
    category_name = models.CharField(max_length=255)

    def __str__(self):
        return self.category_name
    
class Assignments(models.Model):
    title = models.CharField(max_length=255)
    description = QuillField()
    start_date = models.DateTimeField()
    due_date = models.DateTimeField()
    points = models.IntegerField(default=0, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categories')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='classroom_assignments')
    time_limit = models.PositiveIntegerField(default=60)
    attempts = models.PositiveIntegerField(default=1)
    def __str__(self):
        return self.title

class Questions(models.Model):
    assignment = models.ForeignKey(Assignments, on_delete=models.CASCADE, related_name='assignment_questions')
    points = models.FloatField()
    QUESTION_TYPES = [
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('SHORT_ANSWER', 'Short Answer'),
        ('DROPDOWN', 'Dropdown')
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question = QuillField()

    def __str__(self):
        return self.question

class Choices(models.Model):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='question_choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.question

class StudentAnswers(models.Model):
    student_profile = models.ForeignKey(SchoolUserProfile, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='question_answers')
    choice = models.ForeignKey(Choices, on_delete=models.SET_NULL, null=True, blank=True)
    short_answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_profile.user.username} - {self.question}"

class Submissions(models.Model):
    student_profile = models.ForeignKey(SchoolUserProfile, on_delete=models.CASCADE, related_name='student_submission')
    assignment = models.ForeignKey(Assignments, on_delete=models.CASCADE, related_name='submission_answers')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_profile.user.username} - {self.assignment.title} - {self.submitted_at}"
    
class Grades(models.Model):
    student_profile = models.ForeignKey(SchoolUserProfile, on_delete=models.CASCADE, related_name='student_grades')
    assignment = models.ForeignKey(Assignments, on_delete=models.CASCADE, related_name='assignment_grades')
    submission = models.ForeignKey(Submissions, on_delete=models.CASCADE, related_name='submission_grades')
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='classroom_grades')  # New ForeignKey
    grade_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    graded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_profile.user.username} - {self.assignment.title} - Grade: {self.grade_value}"

class Messages(models.Model):
    title = models.CharField(max_length=255)
    text = QuillField()
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    
    def __str__(self):
        return self.title