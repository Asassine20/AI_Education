from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from ai_app.forms import UniversityLogoUploadForm
from ai_app.models import University, SchoolUserProfile
from django.urls import reverse
import os
from django.conf import settings

@login_required
def admin_dashboard(request):
    profile = get_object_or_404(SchoolUserProfile, user=request.user, role='admin')
    return render(request, 'ai_app/dashboards/admin/admin_dashboard.html')


def university_logo_upload_view(request, code):
    university = get_object_or_404(University, code=code, admin=request.user)
    if request.method == 'POST':
        form = UniversityLogoUploadForm(request.POST, university=university)
        if form.is_valid():
            image = form.save(commit=False)
            image.university = university
            image.save()
    else:
        form = UniversityLogoUploadForm(university=university)
    return render(request, 'ai_app/dashboards/admin/image_upload.html', {'form': form, 'university': university})
