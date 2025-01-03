from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from ai_app.models import University, SchoolUserProfile, PairingCode
from ai_app.forms import ParentSignupForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                profile = SchoolUserProfile.objects.get(user=user)
                if profile.role == 'teacher':
                    return redirect('dashboard')
                elif profile.role == 'admin': 
                    return redirect('admin_dashboard')
                elif profile.role == 'student':
                    return redirect('dashboard')
                elif profile.role == 'parent':
                    return redirect('dashboard')

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
                return redirect('dashboard')
            elif school_role == 'admin':
                return redirect('admin_dashboard')
            elif school_role == 'student':
                return redirect('dashboard')
        else:
            login(request, user)
            return redirect('home')
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
            user_profile = SchoolUserProfile.objects.create(user=user, university=university, role=school_role)

            # Generate a pairing code if the role is 'student'
            if school_role == SchoolUserProfile.STUDENT:
                PairingCode.objects.create(student=user_profile)

            login(request, user)
            return redirect('dashboard')

        except IntegrityError:
            return render(request, 'ai_app/auth/school_signup.html', {'error': 'An error occurred. Please try again.'})
        except University.DoesNotExist:
            return render(request, 'ai_app/auth/school_signup.html', {'error_university_code': 'Invalid University Code'})

    return render(request, 'ai_app/auth/school_signup.html')

def parent_signup(request):
    if request.method == 'POST':
        form = ParentSignupForm(request.POST)
        if form.is_valid():
            try:
                # Create the user with the specified role
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                
                pairing_code = form.cleaned_data['pairing_code']
                student_profile = pairing_code.student
                university = student_profile.university  # Retrieve the student's university based on the pairing code
                
                # Create the parent profile and link to student
                user_profile = SchoolUserProfile.objects.create(
                    user=user,
                    university=university,
                    role=SchoolUserProfile.PARENT
                )
                user_profile.students.add(student_profile)
                
                # Log the user in and redirect to the dashboard
                login(request, user)
                return redirect('dashboard')
                
            except IntegrityError:
                form.add_error(None, 'An error occurred while creating your account. Please try again.')
        else:
            # If the form is invalid, render it with error messages
            return render(request, 'ai_app/auth/parent_signup.html', {'form': form})

    # Render an empty form if the request method is GET
    form = ParentSignupForm()
    return render(request, 'ai_app/auth/parent_signup.html', {'form': form})