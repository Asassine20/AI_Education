# ai_app/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from .models import CourseMaterial, Messages, University, SchoolUserProfile, Assignments, Questions, Choices
from django.contrib.auth.forms import UserCreationForm
from django_quill.forms import QuillFormField

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

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
            'start_date': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),  # Ensure this uses DateTimeInput
            'due_date': forms.DateTimeInput(attrs={'class': 'datetimepicker'}),   # Ensure this uses DateTimeInput
        }

    def __init__(self, *args, **kwargs):
        self.classroom = kwargs.pop('classroom', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(AssignmentForm, self).save(commit=False)
        
        if self.classroom:
            instance.classroom = self.classroom
            print(f"Assigned classroom: {self.classroom}")

        if commit:
            instance.save()
            print("Assignment saved!")
        else:
            print("Assignment not saved, commit is False.")
        
        return instance

class QuestionForm(forms.ModelForm):
    question = QuillFormField()
    class Meta:
        model = Questions 
        fields = ['question_type', 'question', 'points']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choices 
        fields = ['choice_text', 'is_correct']

# Formset for Questions
QuestionFormSet = inlineformset_factory(Assignments, Questions, form=QuestionForm, extra=3)

# Formset for Choices (for each Question)
ChoiceFormSet = inlineformset_factory(Questions, Choices, form=ChoiceForm, extra=3)
