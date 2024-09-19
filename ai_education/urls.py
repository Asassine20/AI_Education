from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ai_app.views.teacher_dashboard_views import preview_syllabus

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("ai_app.urls")),  # Include your app URLs
    path('tinymce/', include('tinymce.urls')),
    # Correct URL for syllabus preview with room_code and file_id as arguments
    path('preview-syllabus/<str:room_code>/<int:file_id>/', preview_syllabus, name='preview_syllabus'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
# Serve static files (if needed)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
