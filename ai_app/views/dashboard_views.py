from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom, Question
import uuid  # For generating the class code

@login_required
def teacher_dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='teacher')
    if request.method == 'POST':
        room_name = request.POST['room_name']
        room_code = request.POST['room_code']
        university = profile.university
        new_class = ClassRoom.objects.create(
            room_name=room_name,
            room_code=room_code,
            university=university,
            teacher=request.user
        )
        profile.classes.add(new_class)
        return redirect('teacher_dashboard')

    classes_teaching = profile.classes.all()
    return render(request, 'ai_app/dashboards/teacher_dashboard.html', {'classes_teaching': classes_teaching})


@login_required
def student_dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='student')
    if request.method == 'POST':
        room_code = request.POST['room_code']
        try:
            classroom = ClassRoom.objects.get(room_code=room_code)
            profile.classes.add(classroom)
            return redirect('student_dashboard')
        except ClassRoom.DoesNotExist:
            return render(request, 'ai_app/dashboards/student_dashboard.html', {
                'error': 'Invalid class code',
                'classes': classes
            })

    classes = profile.classes.all()
    return render(request, 'ai_app/dashboards/student_dashboard.html', {'classes': classes})


@login_required
def individual_dashboard(request):
    return render(request, 'ai_app/dashboards/individual_dashboard.html')

@login_required
def add_class(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='teacher')
    
    if request.method == 'POST':
        room_name = request.POST['room_name']
        description = request.POST['description']
        
        # Generate a unique class code
        room_code = uuid.uuid4().hex[:8]  # Use first 8 characters of UUID for the code
        
        # Create the new class
        new_class = ClassRoom.objects.create(
            room_name=room_name,
            description=description,
            room_code=room_code,
            university=profile.university,
            teacher=request.user
        )
        profile.classes.add(new_class)
        return redirect('teacher_dashboard')

    return render(request, 'ai_app/dashboards/add_class.html')

@login_required
def course_page(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)

    # Fetch only the questions related to the classroom
    questions = Question.objects.filter(classroom=classroom)

    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')

    context = {
        'classroom': classroom,
        'students': students,
        'questions': questions,  # Only questions, no responses
    }

    return render(request, 'ai_app/dashboards/course_page.html', context)

@login_required
def students_enrolled(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')
    return render(request, 'ai_app/dashboards/students_enrolled.html', {'classroom': classroom, 'students': students})

@login_required
def student_questions(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    questions = Question.objects.filter(user__schooluserprofile__classes=classroom)
    return render(request, 'ai_app/dashboards/student_questions.html', {'classroom': classroom, 'questions': questions})
