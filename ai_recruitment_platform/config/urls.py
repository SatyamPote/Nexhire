# ai_recruitment_platform/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# --- Views for specific pages ---
class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class FeaturesView(TemplateView): # No login required for features page
    template_name = 'features.html'

class ContactView(TemplateView): # No login required for contact page
    template_name = 'contact.html'

class PrivacyPolicyView(TemplateView): # No login required for privacy policy
    template_name = 'privacy_policy.html'

class SubscriptionView(TemplateView): # No login required for subscription plans
    template_name = 'subscription.html'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('candidates/', include('candidates.urls', namespace='candidates')),
    path('applications/', include('applications.urls', namespace='applications')),

    # --- Root URL ---
    path('', HomePageView.as_view(), name='home'),

    # --- NEW URLS for added pages ---
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)