from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.models import SchoolUserProfile, ClassRoom, Assignments, Messages, CourseMaterial, Questions, Choices, StudentAnswers, Submissions, Grades
from ai_app.forms import inlineformset_factory, MessageUploadForm, AssignmentForm, ChoiceFormSet, ChoiceForm, QuestionForm, CategoryForm, StudentAnswerForm
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.http import FileResponse, JsonResponse, HttpResponseServerError
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import UpdateView, ListView
from django import forms
from datetime import timedelta

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

class EditAssignment(UpdateView):
    model = Assignments
    template_name = 'ai_app/dashboards/teacher/assignments/edit_assignment.html'
    fields = ['title', 'start_date', 'due_date', 'points', 'category', 'time_limit', 'attempts']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add classroom and assignment object to the context
        context['classroom'] = ClassRoom.objects.get(room_code=self.kwargs['room_code'])
        context['assignment'] = self.object  # The current assignment object (self.object is the assignment being edited)
        return context

    # Define the success URL to redirect after form submission
    def get_success_url(self):
        return reverse_lazy('assignments_list', kwargs={'room_code': self.kwargs['room_code']})

# list questions out to edit them
class AssignmentQuestionsListView(ListView):
    model = Questions
    template_name = 'ai_app/dashboards/teacher/assignments/edit_questions_list.html'
    context_object_name = 'questions'

    def get_queryset(self):
        assignment = get_object_or_404(Assignments, pk=self.kwargs['assignment_id'])
        return Questions.objects.filter(assignment=assignment)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignments, pk=self.kwargs['assignment_id'])
        context['classroom'] = get_object_or_404(ClassRoom, room_code=self.kwargs['room_code'])
        return context

class EditQuestionChoicesView(UpdateView):
    model = Questions
    template_name = 'ai_app/dashboards/teacher/assignments/edit_question_choices.html'
    form_class = ChoiceForm

    def get_object(self, queryset=None):
        question_id = self.kwargs.get('question_id')
        return get_object_or_404(Questions, pk=question_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()

        # Inline formset for choices
        ChoiceFormSet = inlineformset_factory(
            Questions, Choices, form=ChoiceForm, extra=0
        )

        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST, instance=question)
        else:
            context['choice_formset'] = ChoiceFormSet(instance=question)

        context['classroom'] = get_object_or_404(ClassRoom, room_code=self.kwargs['room_code'])

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choice_formset = context['choice_formset']

        if form.is_valid() and choice_formset.is_valid():
            self.object = form.save()  # Save the question form
            choice_formset.instance = self.object  # Link the choices to the question
            choice_formset.save()  # Save the choices
            return super().form_valid(form)
        else:
            print("Form or formset is not valid.")  # Debug message
            print(form.errors)  # Output form errors to terminal
            print(choice_formset.errors)  # Output formset errors to terminal
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('assignment_questions', kwargs={
            'room_code': self.kwargs['room_code'],
            'assignment_id': self.kwargs['assignment_id']
        })


class SubmissionsListView(ListView):
    model = Submissions
    template_name = 'ai_app/dashboards/teacher/assignments/assignment_submissions_list.html'

    def get_queryset(self):
        assignment_id = self.kwargs['assignment_id']  # Get assignment_id from URL
        return Submissions.objects.filter(assignment_id=assignment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = get_object_or_404(Assignments, pk=self.kwargs['assignment_id'])
        context['classroom'] = get_object_or_404(ClassRoom, room_code=self.kwargs['room_code'])
        return context

    
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
    
    questions = assignment.assignment_questions.all()
    form = StudentAnswerForm(request.POST or None, questions=questions)

    # Convert time_limit (minutes) to time_limit_seconds
    time_limit_seconds = assignment.time_limit * 60  # Convert the time limit to seconds

    if request.method == 'POST' and form.is_valid():
        # Save student answers and create submission record
        for question in questions:
            field_name = f"question_{question.id}"
            answer_data = form.cleaned_data.get(field_name)

            if question.question_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
                # Skip if no choice was made (empty answer_data)
                if answer_data:  # Ensure it's not an empty string or None
                    selected_choice = Choices.objects.filter(id=answer_data).first()  # Use .filter().first() to avoid errors
                    if selected_choice:
                        StudentAnswers.objects.create(
                            student_profile=user_profile,
                            question=question,
                            choice=selected_choice
                        )
            elif question.question_type == 'SHORT_ANSWER':
                # Handle short answer question
                if answer_data:  # Only save if the student provided an answer
                    StudentAnswers.objects.create(
                        student_profile=user_profile,
                        question=question,
                        short_answer=answer_data
                    )

        # Create a submission record
        Submissions.objects.create(student_profile=user_profile, assignment=assignment)

        return redirect('assignment_page', room_code=room_code, assignment_id=assignment_id)

    # Pass time_limit_seconds to the template
    return render(request, 'ai_app/dashboards/teacher/assignments/submit_assignment.html', {
        'assignment': assignment,
        'classroom': classroom,
        'question_form_pairs': zip(questions, form),
        'time_limit_seconds': time_limit_seconds,  # Pass the calculated time limit in seconds
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