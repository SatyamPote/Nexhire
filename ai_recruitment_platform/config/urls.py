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

class FeaturesView(TemplateView):
    template_name = 'features.html'

class ContactView(TemplateView):
    template_name = 'contact.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'privacy_policy.html'

class SubscriptionView(TemplateView):
    template_name = 'subscription.html'

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- Allauth URLs ---
    # This is the standard inclusion. It should automatically handle account and social URLs.
    # Ensure this is the ONLY place 'allauth' URLs are included at the root level.
    path('accounts/', include('allauth.urls')),

    # --- DO NOT EXPLICITLY INCLUDE socialaccount.urls here with a namespace ---
    # The error "Specifying a namespace in include() without providing an app_name"
    # means allauth.socialaccount.urls does not define an app_name, so you
    # cannot assign a namespace to it this way. Rely on the main allauth.urls inclusion.

    # --- Our Custom App URLs ---
    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('candidates/', include('candidates.urls', namespace='candidates')),
    path('applications/', include('applications.urls', namespace='applications')),

    # --- Root URL ---
    path('', HomePageView.as_view(), name='home'),

    # ai_recruitment_platform/config/urls.py
    path('users/', include('users.urls', namespace='users')), # Ensure this is present

    # --- Added URLs for static pages ---
    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

