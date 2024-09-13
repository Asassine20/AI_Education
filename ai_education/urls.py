from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("ai_app.urls")),  # Include your app URLs
]

# Serving media files during development
if settings.DEBUG:  # This ensures that media files are only served during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Serving static files (usually handled automatically if settings are correct)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
