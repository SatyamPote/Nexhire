# ai_recruitment_platform/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# <<< ADD THIS IMPORT >>>
from django.contrib.auth.mixins import LoginRequiredMixin
# <<< END ADDITION >>>
from django.views.generic import TemplateView


# --- Create a simple homepage view ---
class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html' # We'll create this template


urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Authentication URLs ---
    # Include allauth's URLs for login, signup, logout, password reset, etc.
    path('accounts/', include('allauth.urls')),

    # --- Our Apps URLs ---
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('candidates/', include('candidates.urls', namespace='candidates')),
    # path('applications/', include('applications.urls', namespace='applications')),

    # --- Homepage URL ---
    # Map root URL to our homepage view
    path('', HomePageView.as_view(), name='home'),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)