# ai_app/forms.py
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import CourseMaterial, ClassRoom, Messages, University, SchoolUserProfile, Assignments, Questions, Choices, Category, StudentAnswers, PairingCode
from django.contrib.auth.forms import UserCreationForm
from django_quill.forms import QuillFormField

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class ParentSignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    pairing_code = forms.CharField(max_length=10, help_text="Enter your student's pairing code.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_pairing_code(self):
        code = self.cleaned_data.get('pairing_code')
        try:
            pairing_code = PairingCode.objects.get(code=code)
        except PairingCode.DoesNotExist:
            raise forms.ValidationError("Invalid pairing code.")
        return pairing_code

    def clean_pairing_code(self):
        code = self.cleaned_data.get('pairing_code')
        try:
            # Retrieve the PairingCode instance if it exists
            pairing_code = PairingCode.objects.get(code=code)
        except PairingCode.DoesNotExist:
            raise forms.ValidationError("Invalid pairing code.")
        return pairing_code
    
class JoinClassForm(forms.Form):
    room_code = forms.CharField(max_length=50)
    room_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        room_code = cleaned_data.get('room_code')
        room_password = cleaned_data.get('room_password')

        if room_code and room_password:
            # Try to find a classroom with the provided room code
            try:
                classroom = ClassRoom.objects.get(room_code=room_code)
                
                # If the room code is correct, check the password
                if classroom.room_password != room_password:
                    raise ValidationError('Incorrect password for the classroom.')
            
            except ClassRoom.DoesNotExist:
                raise ValidationError('Classroom with this room code does not exist.')

        return cleaned_data

class FileUploadForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[], required=False, label="Select Category")
    new_category = forms.CharField(max_length=255, required=False, label="Add New Category")
    display_name = forms.CharField(max_length=255, required=True)
    
    class Meta:
        model = CourseMaterial
        fields = ['file', 'display_name', 'category', 'new_category', 'visible_to_students', 'is_syllabus']
    
    def __init__(self, *args, **kwargs):
        classroom = kwargs.pop('classroom', None)
        super().__init__(*args, **kwargs)
        # Get distinct categories from the CourseMaterial model
        existing_categories = CourseMaterial.objects.filter(classroom=classroom).values_list('category', flat=True).distinct()
        category_choices = [(cat, cat) for cat in existing_categories if cat]
        self.fields['category'].choices = [('', 'Select a category')] + category_choices

class MessageUploadForm(forms.ModelForm):
    text = QuillFormField()
    class Meta:
        model = Messages
        fields = ['title', 'text']
    
    # Automatically gets the classroom for the form
    def __init__(self, *args, **kwargs):
        self.classroom = kwargs.pop('classroom', None)
        super(MessageUploadForm, self).__init__(*args, **kwargs)
                                    
class UniversityLogoUploadForm(forms.ModelForm):
    class Meta:
        model = University
        fields = ['logo']
    
    def __init__(self, *args, **kwargs):
        # Extract 'university' from kwargs
        self.university = kwargs.pop('university', None)
        super(UniversityLogoUploadForm, self).__init__(*args, **kwargs)

class ProfileImageUploadForm(forms.ModelForm):
    class Meta:
        model = SchoolUserProfile
        fields = ['profile_image']

class AssignmentForm(forms.ModelForm):
    description = QuillFormField()
    class Meta:
        model = Assignments
        fields = ['title', 'description', 'start_date', 'due_date', 'category', 'points']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),
        }

    def __init__(self, *args, **kwargs):
        self.classroom = kwargs.pop('classroom', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.classroom:
            instance.classroom = self.classroom
        if commit:
            instance.save()
        return instance

class QuestionForm(forms.ModelForm):
    question = QuillFormField()
    class Meta:
        model = Questions
        fields = ['question_type', 'question', 'points']

class ChoiceForm(forms.ModelForm):
    choice_text = forms.CharField(required=False)
    class Meta:
        model = Choices
        fields = ['choice_text', 'is_correct']

ChoiceFormSet = inlineformset_factory(
    Questions, Choices, form=ChoiceForm, 
    fields=['choice_text', 'is_correct'], extra=4, can_delete=True)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'points']

class StudentAnswerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)

        for question in questions:
            field_name = f"question_{question.id}"

            # Check for the type of question and add the corresponding form field
            if question.question_type in ['MULTIPLE_CHOICE', 'DROPDOWN']:
                # Prepare choices for multiple-choice or dropdown questions
                choices = [(choice.id, choice.choice_text) for choice in question.question_choices.all()]
                widget = forms.RadioSelect if question.question_type == 'MULTIPLE_CHOICE' else forms.Select
                # Using .html attribute for QuillField content if available
                label = question.question.html if hasattr(question.question, 'html') else question.question

                # Allow the question to be optional by setting required=False
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    widget=widget,
                    label=label,
                    required=False  # Make the field optional
                )
            elif question.question_type == 'SHORT_ANSWER':
                # Use a Textarea widget for short-answer questions
                label = question.question.html if hasattr(question.question, 'html') else question.question

                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea,
                    label=label,
                    required=False  # Make short-answer questions optional as well
                )

class StudentAnswerGradeForm(forms.ModelForm):
    class Meta:
        model = StudentAnswers
        fields = ['points_earned']

StudentAnswerGradeFormSet = modelformset_factory(
    StudentAnswers,
    form=StudentAnswerGradeForm,
    extra=0,
)
