from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.forms import ProfileImageUploadForm
from ai_app.models import SchoolUserProfile
def home(request):
    return render(request, 'ai_app/main/home.html')

def landing_page(request):
    return render(request, 'ai_app/main/landingpage.html')

def contact_view(request):
    return render(request, 'ai_app/contact.html')

@login_required
def profile_image_upload_view(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    if request.method == 'POST':
        form = ProfileImageUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            # Redirect based on the user's role
            if profile.role == 'admin':
                return redirect('admin_dashboard')
            elif profile.role == 'teacher':
                return redirect('dashboard')
            elif profile.role == 'student':
                return redirect('dashboard')    
    else:
        form = ProfileImageUploadForm(instance=profile)
    
    return render(request, 'ai_app/dashboards/profile_image_upload.html', {
        'form': form
    })