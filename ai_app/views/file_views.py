from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from ai_app.forms import FileUploadForm
from ai_app.models import CourseMaterial, ClassRoom, SchoolUserProfile
from django.urls import reverse
import os
from django.conf import settings
from django.http import FileResponse
from urllib.parse import unquote

def file_upload_view(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code, teacher=request.user)
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, classroom=classroom)
        if form.is_valid():
            material = form.save(commit=False)
            material.classroom = classroom
            material.professor = request.user
            material.course_name = classroom.room_code
            new_category = form.cleaned_data.get('new_category')

            if new_category:
                material.category = new_category
            else:
                material.category =form.cleaned_data.get('category')
            
            if 'set_as_syllabus' in request.POST:
                CourseMaterial.objects.filter(classroom=classroom, professor=request.user, is_syllabus=True).update(is_syllabus=False)
                material.is_syllabus = True
            material.material = request.FILES['file']
            material.save()
            return redirect(reverse('file_list', kwargs={'room_code': room_code}))
    else:
        form = FileUploadForm(classroom=classroom)
    return render(request, 'ai_app/dashboards/teacher/files/file_upload.html', {'form': form, 'classroom': classroom})

def file_edit_view(request, room_code, file_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code, teacher=request.user)
    material = get_object_or_404(CourseMaterial, id=file_id, classroom=classroom)

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            return redirect(reverse('file_list', kwargs={'room_code': room_code}))
    else:
        form = FileUploadForm(instance=material)

    return render(request, 'ai_app/dashboards/teacher/files/file_edit.html', {'form': form, 'classroom': classroom})

def file_list_view(request, room_code):
    classroom = get_object_or_404(ClassRoom, room_code=room_code)
    user_profile = get_object_or_404(SchoolUserProfile, user=request.user)
    if user_profile.role == SchoolUserProfile.TEACHER:
        files = CourseMaterial.objects.filter(classroom=classroom)
    else:
        files = CourseMaterial.objects.filter(classroom=classroom, visible_to_students=True)

    return render(request, 'ai_app/dashboards/teacher/files/file_list.html', {'files': files, 'classroom': classroom})

def file_download_view(request, room_code, file_id):
    classroom = get_object_or_404(ClassRoom, room_code=room_code, teacher=request.user)
    file = get_object_or_404(CourseMaterial, id=file_id, classroom=classroom)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

def file_preview_view(request, room_code, display_name):
    classroom = get_object_or_404(ClassRoom, room_code=room_code, teacher=request.user)
    decoded_display_name = unquote(display_name)
    file = get_object_or_404(CourseMaterial, display_name=decoded_display_name, classroom=classroom)
    file_path = os.path.join(settings.MEDIA_ROOT,file.file.name)
    if file.file.name.endswith(('.png', '.jpg', '.jpeg')):
        return render(request, 'ai_app/dashboards/teacher/files/file_preview.html', {'file': file, 'classroom': classroom})
    return HttpResponse("Preview not available for this file type")