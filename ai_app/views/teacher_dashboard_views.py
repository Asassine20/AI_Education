from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom, Assignments, Messages, CourseMaterial, Questions, Choices, StudentAnswers, Submissions, Grades
from ai_app.forms import inlineformset_factory, MessageUploadForm, AssignmentForm, ChoiceFormSet, ChoiceForm, QuestionForm, CategoryForm, StudentAnswerForm
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponseServerError
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
import os

@login_required
def dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    university = profile.university
    profile_image = profile.profile_image
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
        return redirect('dashboard')

    classes = profile.classes.all()
    return render(request, 'ai_app/dashboards/teacher/dashboard/teacher_dashboard.html', {
        'classes': classes,
        'university': university,
        'profile_image': profile_image,
    })



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
        return redirect('dashboard')

    return render(request, 'ai_app/dashboards/teacher/dashboard/add_class.html')

@login_required
def join_class(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='student')
    if request.method == 'POST':
        room_code = request.POST['room_code']
        try:
            classroom = ClassRoom.objects.get(room_code=room_code)
            profile.classes.add(classroom)
            return redirect('dashboard')
        except ClassRoom.DoesNotExist:
            return render(request, 'ai_app/dashboards/teacher/dashboard/teacher_dashboard.html', {
                'error': 'Invalid class code',
            })
    
    return render(request, 'ai_app/dashboards/teacher/dashboard/join_class.html')
    
@login_required
def course_page(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    syllabus = CourseMaterial.objects.filter(classroom=classroom, is_syllabus=True).first()
    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')
    
    return render(request, 'ai_app/dashboards/teacher/course_page.html',{
        'classroom': classroom,
        'students': students,
        'syllabus': syllabus,
    })

@login_required
def students_enrolled(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    students = SchoolUserProfile.objects.filter(classes=classroom, role='student')
    return render(request, 'ai_app/dashboards/teacher/students/students_enrolled.html', {'classroom': classroom, 'students': students})

@login_required
def messages_list(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    messages = Messages.objects.filter(classroom=classroom).select_related('user__schooluserprofile')
    return render(request, 'ai_app/dashboards/teacher/messages/messages_list.html', {
        'classroom': classroom, 
        'messages': messages,
        })

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
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    if request.method == 'POST':
        form = MessageUploadForm(request.POST, classroom=classroom)
        if form.is_valid():
            message = form.save(commit=False)
            message.classroom = classroom
            message.user = request.user
            message.save()
            return redirect('messages_list', room_code=room_code)
    else:
        form = MessageUploadForm()
    return render(request, 'ai_app/dashboards/teacher/messages/create_message.html', {
        'form': form, 
        'classroom': classroom
    })

@login_required
def download_syllabus(request, room_code, file_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    file = get_object_or_404(CourseMaterial, classroom=classroom, id=file_id, is_syllabus=True)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

@xframe_options_exempt
def preview_syllabus(request, room_code, file_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    file = get_object_or_404(CourseMaterial, classroom=classroom, id=file_id, is_syllabus=True)
    # Check if the file is a PDF
    if file.file.name.endswith('.pdf'):
        try:
            return FileResponse(open(file.file.path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404("File not found")
    else:
        return Http404("Syllabus is not a PDF")
    
def assignment_create(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    return render(request, 'ai_app/dashboards/teacher/assignments/assignment_form.html', {
        'form': form,
        'classroom': classroom
    })

def question_create(request, room_code, assignment_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    assignment = get_object_or_404(Assignments, pk=assignment_id, classroom=classroom)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()
            if question.question_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
                formset = ChoiceFormSet(request.POST, instance=question)
                if formset.is_valid():
                    formset.save()
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()
    return render(request, 'ai_app/dashboards/teacher/assignments/question_form.html', {
        'form': form,
        'formset': formset,
        'assignment': assignment,
        'classroom': classroom
    })

def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignments, pk=pk)
    questions = assignment.assignment_questions.all()
    classroom = assignment.classroom  # Get the classroom if needed

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = ChoiceFormSet(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.assignment = assignment
            question.save()
            if question.question_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
                formset = ChoiceFormSet(request.POST, instance=question)
                if formset.is_valid():
                    formset.save()
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = QuestionForm()
        formset = ChoiceFormSet()

    return render(request, 'ai_app/dashboards/teacher/assignments/assignment_detail.html', {
        'assignment': assignment,
        'questions': questions,
        'form': form,
        'formset': formset,
        'classroom': classroom,  # Include if needed in the template
    })

@login_required
def assignments_list(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    
    # Get all assignments for the classroom, ordered by due date
    assignments = Assignments.objects.filter(classroom=classroom).order_by('due_date')
    
    # Get the list of submitted assignments for the user in the current classroom
    submitted_assignments = Submissions.objects.filter(assignment__in=assignments, student_profile=profile).values_list('assignment_id', flat=True)

    # Annotate each assignment with a submitted flag
    for assignment in assignments:
        assignment.submitted = assignment.id in submitted_assignments

    # Separate upcoming and past assignments
    current_time = timezone.now()
    upcoming_assignments = [assignment for assignment in assignments if assignment.due_date >= current_time]
    past_assignments = [assignment for assignment in assignments if assignment.due_date < current_time]

    return render(request, 'ai_app/dashboards/teacher/assignments/assignments_list.html', {
        'classroom': classroom, 
        'upcoming_assignments': upcoming_assignments,
        'past_assignments': past_assignments,
        'room_code': room_code,
    })

@login_required
def delete_assignment(request, room_code, assignment_id):
    assignment = get_object_or_404(Assignments, id=assignment_id)
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignments_list', room_code=room_code)
    return render(request, 'ai_app/dashboards/teacher/assignments/assignments_list.html',{
        'assignment': assignment,
    })

@login_required
def assignment_page(request, room_code, assignment_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    assignment = get_object_or_404(Assignments, classroom=classroom, id=assignment_id)
    try:
        submission = Submissions.objects.get(assignment=assignment, student_profile=profile)
    except Submissions.DoesNotExist:
        submission = None
    current_time = timezone.now()
    before_start = current_time < assignment.start_date
    after_due = current_time > assignment.due_date
    show_questions = assignment.start_date <= current_time <= assignment.due_date
    return render(request, 'ai_app/dashboards/teacher/assignments/assignment_page.html',{
        'classroom': classroom,
        'assignment': assignment,
        'show_questions': show_questions,
        'after_due': after_due,
        'before_start': before_start,
        'submission': submission
    })

@login_required
def submit_assignment(request, room_code, assignment_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    assignment = get_object_or_404(Assignments, id=assignment_id, classroom=classroom)
    user_profile = get_object_or_404(SchoolUserProfile, user=request.user, role=SchoolUserProfile.STUDENT)
    #profile = get_object_or_404(SchoolUserProfile, user=request.user, role='teacher')

    questions = assignment.assignment_questions.all()
    form = StudentAnswerForm(request.POST or None, questions=questions)

    # Zip questions and form fields together
    question_form_pairs = zip(questions, form)

    if request.method == 'POST' and form.is_valid():
        for question in questions:
            field_name = f"question_{question.id}"
            answer_data = form.cleaned_data.get(field_name)

            if question.question_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
                selected_choice = Choices.objects.get(id=answer_data)
                StudentAnswers.objects.create(
                    student_profile=user_profile,
                    question=question,
                    choice=selected_choice
                )
            elif question.question_type == 'SHORT_ANSWER':
                StudentAnswers.objects.create(
                    student_profile=user_profile,
                    question=question,
                    short_answer=answer_data
                )

        # Create a submission record
        Submissions.objects.create(student_profile=user_profile, assignment=assignment)

        return redirect('assignment_page', room_code=room_code, assignment_id=assignment_id)

    return render(request, 'ai_app/dashboards/teacher/assignments/submit_assignment.html', {
        'assignment': assignment,
        'classroom': classroom,
        'question_form_pairs': question_form_pairs  # Pass the zipped pairs
    })

@login_required
def view_submissions(request, room_code, assignment_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    assignment = get_object_or_404(Assignments, id=assignment_id, classroom=classroom)
    submissions = Submissions.objects.filter(assignment=assignment)

    students_with_submissions = {
        submission.student_profile: submission for submission in submissions
    }

    # List all students in the class, check if they have submitted or not
    all_students = classroom.students.all()
    student_submission_status = [
        {
            'student': student,
            'submission': students_with_submissions.get(student.schooluserprofile, None)
        }
        for student in all_students
    ]

    return render(request, 'ai_app/dashboards/teacher/assignments/view_submissions.html', {
        'assignment': assignment,
        'classroom': classroom,
        'student_submission_status': student_submission_status,
    })


@login_required
def grades_list(request, room_code):
    # Fetch the classroom based on room_code
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    
    # Fetch the student's profile for the logged-in user
    student_profile = get_object_or_404(SchoolUserProfile, user=request.user)

    # Filter grades by student profile and classroom, including assignment details for easy access in the template
    graded_assignments = Grades.objects.filter(
        student_profile=student_profile,
        classroom=classroom
    ).select_related('assignment', 'submission')

    # Render the template with the context data
    return render(request, 'ai_app/dashboards/teacher/grades/grades_list.html', {
        'classroom': classroom,
        'graded_assignments': graded_assignments,
    })

@login_required
def add_category(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.classroom = classroom
            category.save()
            return redirect('assignment_create', room_code=room_code)
    else:
        form = CategoryForm()
    return render(request, 'ai_app/dashboards/teacher/assignments/add_category.html', {
        'form': form,
        'classroom': classroom
    })