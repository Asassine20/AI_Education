from django.shortcuts import render, redirect
from django.http import HttpResponse
from ai_app.forms import FileUploadForm
from ai_app.models import CourseMaterial
import os
from django.conf import settings
from django.http import FileResponse

def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    return render(request, 'ai_app/files/file_upload.html', {'form': form})

def file_list_view(request):
    files = CourseMaterial.objects.all()
    return render(request, 'ai_app/files/file_list.html', {'files': files})

def file_download_view(request, file_id):
    file = CourseMaterial.objects.get(id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
    return FileResponse(open(file_path, 'rb'), as_attachment=True)

def file_preview_view(request, file_id):
    file = CourseMaterial.objects.get(id=file_id)
    file_path = os.path.join(settings.MEDIA_ROOT,file.file.name)
    if file.file.name.endswith(('.png', '.jpg', '.jpeg')):
        return render(request, 'ai_app/files/file_preview.html', {'file': file})
    return HttpResponse("Preview not available for this file type")