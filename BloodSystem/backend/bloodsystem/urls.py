"""
URL configuration for bloodsystem project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/donor/', include('donor.urls')),
    path('api/hospital/', include('hospital.urls')),
    path('api/camp/', include('camp.urls')),
    path('api/patient/', include('patient.urls')),
    path('api/admin/', include('adminpanel.urls')),
    path('api/notifications/', include('notifications.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)