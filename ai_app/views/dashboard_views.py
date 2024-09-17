from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom, Question, Assignment, Messages
from ai_app.forms import MessageUploadForm
from django.urls import reverse
from django.contrib import messages

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
    return render(request, 'ai_app/dashboards/teacher/teacher_dashboard.html', {'classes_teaching': classes_teaching})


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
            return render(request, 'ai_app/dashboards/student/student_dashboard.html', {
                'error': 'Invalid class code',
                'classes': classes
            })

    classes = profile.classes.all()
    return render(request, 'ai_app/dashboards/student/student_dashboard.html', {'classes': classes})

@login_required
def add_class(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='teacher')

    if request.method == 'POST':
        room_name = request.POST['room_name']
        description = request.POST['description']
        room_code = request.POST['room_code']
        room_number = request.POST['room_number']

        # Get the class times
        days = request.POST.getlist('days[]')
        start_times = request.POST.getlist('start_times[]')
        start_periods = request.POST.getlist('start_periods[]')
        end_times = request.POST.getlist('end_times[]')
        end_periods = request.POST.getlist('end_periods[]')

        class_times = {}
        for day, start_time, start_period, end_time, end_period in zip(days, start_times, start_periods, end_times, end_periods):
            class_times[day] = f'{start_time} {start_period} - {end_time} {end_period}'

        # Create the new class
        new_class = ClassRoom.objects.create(
            room_name=room_name,
            description=description,
            room_code=room_code,
            university=profile.university,
            teacher=request.user,
            room_number=room_number,
            class_times=class_times 
        )

        profile.classes.add(new_class)
        return redirect('teacher_dashboard')

    return render(request, 'ai_app/dashboards/teacher/add_class.html')



@login_required
def course_page(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)

    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')

    context = {
        'classroom': classroom,
        'students': students,
    }

    return render(request, 'ai_app/dashboards/teacher/course_page.html', context)


@login_required
def students_enrolled(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')
    return render(request, 'ai_app/dashboards/teacher/students_enrolled.html', {'classroom': classroom, 'students': students})


@login_required
def student_questions(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    questions = Question.objects.filter(user__schooluserprofile__classes=classroom)
    return render(request, 'ai_app/dashboards/teacher/student_questions.html', {'classroom': classroom, 'questions': questions})


@login_required
def students_in_class(request, room_code):
    """
    Looks through ClassRoom table to see if room_code exists. 
    Filters through SchoolUserProfile to find all students in the class.
    Renders the HTML page students_in_class.html and passes classroom and students data to the template.
    """
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')
    return render(request, 'ai_app/dashboards/students/students_in_class.html', {'classroom': classroom, 'students': students})


@login_required
def assignments_in_class(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    assignments = Assignment.objects.filter(classroom=classroom)
    return render(request, 'ai_app/dashboards/students/assignments_in_class.html', {'classroom': classroom, 'assignments': assignments})


@login_required
def grades_in_class(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    # Assuming a Grade model exists
    grades = Grade.objects.filter(classroom=classroom)
    return render(request, 'ai_app/dashboards/grades_in_class.html', {'classroom': classroom, 'grades': grades})


@login_required
def syllabus_in_class(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    return render(request, 'ai_app/dashboards/syllabus_in_class.html', {'classroom': classroom})


@login_required
def subjects_in_class(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    # Assuming a Subject model exists
    subjects = Subject.objects.filter(classroom=classroom)
    return render(request, 'ai_app/dashboards/students/subjects_in_class.html', {'classroom': classroom, 'subjects': subjects})

@login_required
def messages_list(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    messages = Messages.objects.filter(classroom=classroom)
    return render(request, 'ai_app/dashboards/teacher/messages_list.html', {'classroom': classroom, 'messages': messages})

@login_required
def delete_message(request, room_code, message_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    message = get_object_or_404(Messages, id=message_id, classroom=classroom)
    if request.method == 'POST':
        message.delete()
        return redirect(reverse('messages_list', kwargs={'room_code': room_code}))
    return render(request, 'ai_app/dashboards/teacher/confirm_delete.html', {'message': message, 'classroom': classroom})

@login_required
def create_message(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code, teacher=request.user)
    if request.method == 'POST':
        form = MessageUploadForm(request.POST, classroom=classroom)
        if form.is_valid():
            message = form.save(commit=False)
            message.classroom = classroom
            message.professor = request.user
            message.course_name = classroom.room_code
            message.save()
            return redirect(reverse('messages_list', kwargs={'room_code': room_code}))
    else:
        form = MessageUploadForm(classroom=classroom)
    return render(request, 'ai_app/dashboards/teacher/create_message.html', {'form': form, 'classroom': classroom})