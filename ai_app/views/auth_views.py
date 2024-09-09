from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from ai_app.models import University, SchoolUserProfile

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                try:
                    profile = SchoolUserProfile.objects.get(user=user)
                    if profile.role == 'teacher':
                        return redirect('teacher_dashboard')
                    elif profile.role == 'student':
                        return redirect('student_dashboard')
                except SchoolUserProfile.DoesNotExist:
                    return redirect('individual_dashboard')

    else:
        form = AuthenticationForm()
    return render(request, 'ai_app/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user_type = request.POST.get('user_type')

        user = User.objects.create_user(username=username, email=email, password=password)

        if user_type == 'school':
            university_code = request.POST['university_code']
            school_role = request.POST['school_role']
            try:
                university = University.objects.get(code=university_code)
                SchoolUserProfile.objects.create(user=user, university=university, role=school_role)
            except University.DoesNotExist:
                return render(request, 'ai_app/school_signup.html', {'error': 'Invalid University Code'})

            if school_role == 'teacher':
                return redirect('teacher_dashboard')
            elif school_role == 'student':
                return redirect('student_dashboard')
        else:
            login(request, user)
            return redirect('home')

    if request.GET.get('user_type') == 'individual':
        return render(request, 'ai_app/auth/individual_signup.html')
    return render(request, 'ai_app/auth/signup.html')


def school_signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        university_code = request.POST['university_code']
        school_role = request.POST['school_role']

        if User.objects.filter(username=username).exists():
            return render(request, 'ai_app/auth/school_signup.html', {'error_username': 'This username is already taken'})
        if User.objects.filter(email=email).exists():
            return render(request, 'ai_app/auth/school_signup.html', {'error_email': 'An account with this email already exists'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            university = University.objects.get(code=university_code)
            SchoolUserProfile.objects.create(user=user, university=university, role=school_role)
            login(request, user)
            return redirect('home')

        except IntegrityError:
            return render(request, 'ai_app/auth/school_signup.html', {'error': 'An error occurred. Please try again.'})
        except University.DoesNotExist:
            return render(request, 'ai_app/auth/school_signup.html', {'error_university_code': 'Invalid University Code'})

    return render(request, 'ai_app/auth/school_signup.html')


def individual_signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'ai_app/auth/individual_signup.html')
