# ai_recruitment_platform/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),

    # --- Include app-specific URLs here ---
    # Example: path('jobs/', include('jobs.urls')),
    # Example: path('candidates/', include('candidates.urls')),
    # Example: path('applications/', include('applications.urls')),
    # Example: path('accounts/', include('allauth.urls')), # For authentication

    # Placeholder for API URLs if using DRF
    # path('api/', include('api.urls')), # Assuming an 'api' app for DRF

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)