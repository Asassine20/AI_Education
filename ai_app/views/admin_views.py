from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ai_app.forms import UniversityLogoUploadForm
from ai_app.models import University, SchoolUserProfile
from django.contrib.auth import logout

@login_required
def admin_dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='admin')
    university = profile.university
    print(university.logo)
    return render(request, 'ai_app/dashboards/admin/admin_dashboard.html', {
        'university': university
    })

@login_required
def university_logo_upload_view(request, code):
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    university = get_object_or_404(University, code=code)
    if request.method == 'POST':
        form = UniversityLogoUploadForm(request.POST, request.FILES, instance=university)
        if form.is_valid():
            image = form.save(commit=False)
            image.university = university
            image.save()
            return redirect('admin_dashboard')
    else:
        form = UniversityLogoUploadForm(instance=university)
    
    return render(request, 'ai_app/dashboards/admin/image_upload.html', {
        'form': form, 
        'university': university
    })

@login_required
def display_logo(request, code):
    profile = get_object_or_404(SchoolUserProfile, user=request.user)
    university = profile.university
    return {
        'university': university
    }

def logout_view(request):
    logout(request)
    return redirect('/')