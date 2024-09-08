from openai import OpenAI
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, CourseMaterial, University, SchoolUserProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import SignUpForm

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        user = request.user

        try:
            # Use the ChatCompletion API for chat-based models
            response = client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an educational assistant."},
                    {"role": "user", "content": f"Explain the topic '{topic}' in detail for a student to understand."}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Extract the response text
            ai_response = response.choices[0].message.content

            # Store the question and response
            Question.objects.create(user=user, topic=topic, response=ai_response)

            return JsonResponse({'response': ai_response})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'ai_app/home.html')

@login_required
def upload_materials(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        material = request.POST.get('material')
        professor = request.user

        CourseMaterial.objects.create(professor=professor, course_name=course_name, material=material)

        return JsonResponse({'message': 'Course material uploaded successfully'})

    return render(request, 'ai_app/upload_materials.html')

@login_required
def view_questions(request):
    questions = Question.objects.all().order_by('-timestamp')
    return render(request, 'ai_app/questions.html', {'questions': questions})


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user_type = request.POST.get('user_type')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Check if it's a school user or individual user
        if user_type == 'school':
            university_code = request.POST['university_code']
            school_role = request.POST['school_role']
            try:
                university = University.objects.get(code=university_code)
                # Create school-specific user profile
                SchoolUserProfile.objects.create(user=user, university=university, role=school_role)
            except University.DoesNotExist:
                return render(request, 'ai_app/school_signup.html', {'error': 'Invalid University Code'})
        else:
            # If it's an individual user, just save the user
            pass

        # Log in the user automatically
        login(request, user)
        return redirect('home')

    # Check which user type to render the correct template
    if request.GET.get('user_type') == 'individual':
        return render(request, 'ai_app/individual_signup.html')
    return render(request, 'ai_app/signup.html')
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'ai_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'ai_app/home.html')

def landing_page(request):
    return render(request, 'ai_app/landingpage.html')

def contact_view(request):
    return render(request, 'ai_app/contact.html')
def school_signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        university_code = request.POST['university_code']
        school_role = request.POST['school_role']

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        try:
            university = University.objects.get(code=university_code)
            # Create school-specific user profile
            SchoolUserProfile.objects.create(user=user, university=university, role=school_role)
        except University.DoesNotExist:
            return render(request, 'ai_app/school_signup.html', {'error': 'Invalid University Code'})

        # Log in the user automatically
        login(request, user)
        return redirect('home')

    return render(request, 'ai_app/school_signup.html')

def individual_signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Log in the user automatically
        login(request, user)
        return redirect('home')

    return render(request, 'ai_app/individual_signup.html')
