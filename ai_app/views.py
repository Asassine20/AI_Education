from openai import OpenAI
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Question, CourseMaterial
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm

# Initialize the OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def ask_question(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        user = request.user

        try:
            # Corrected: Use the ChatCompletion API for chat-based models
            response = client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are an educational assistant."},
                    {"role": "user", "content": f"Explain the topic '{topic}' in detail for a student to understand."}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Extract the response text using the correct access method
            ai_response = response.choices[0].message.content

            # Store the question and response
            Question.objects.create(user=user, topic=topic, response=ai_response)

            return JsonResponse({'response': ai_response})

        except Exception as e:
            # Handle OpenAI API errors gracefully
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
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')  # Redirect to home page after sign-up
    else:
        form = SignUpForm()
    return render(request, 'ai_app/signup.html', {'form': form})

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