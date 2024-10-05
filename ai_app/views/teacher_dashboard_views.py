from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom, Question, Assignments, Messages, CourseMaterial, Questions, Choices
from ai_app.forms import inlineformset_factory, MessageUploadForm, AssignmentForm, ChoiceFormSet, ChoiceForm, QuestionForm, CategoryForm
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponseServerError
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
import os
import pprint

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
    assignments = Assignments.objects.filter(classroom=classroom).order_by('due_date')

    current_time = timezone.now()
    upcoming_assignments = assignments.filter(due_date__gte=current_time)
    past_assignments = assignments.filter(due_date__lt=current_time)

    return render(request, 'ai_app/dashboards/teacher/assignments/assignments_list.html', {
        'classroom': classroom, 
        'upcoming_assignments': upcoming_assignments,
        'past_assignments': past_assignments,
    })

@login_required
def assignment_page(request, room_code, assignment_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    assignment = get_object_or_404(Assignments, classroom=classroom, id=assignment_id)
    questions = Questions.objects.filter(assignment_id=assignment_id)
    current_time = timezone.now()
    before_start = current_time < assignment.start_date
    after_due = current_time > assignment.due_date
    show_questions = assignment.start_date <= current_time <= assignment.due_date
    return render(request, 'ai_app/dashboards/teacher/assignments/assignment_page.html',{
        'classroom': classroom,
        'assignment': assignment,
        'questions': questions,
        'show_questions': show_questions,
        'after_due': after_due,
        'before_start': before_start,
    })