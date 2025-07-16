# ai_recruitment_platform/config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

class FeaturesView(TemplateView): template_name = 'features.html'
class ContactView(TemplateView): template_name = 'contact.html'
class PrivacyPolicyView(TemplateView): template_name = 'privacy_policy.html'
class SubscriptionView(TemplateView): template_name = 'subscription.html'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),
    path('accounts/social/', include('allauth.socialaccount.urls', namespace='social')),

    path('jobs/', include('jobs.urls', namespace='jobs')),
    path('candidates/', include('candidates.urls', namespace='candidates')),
    path('applications/', include('applications.urls', namespace='applications')),
    path('users/', include('users.urls', namespace='users')),

    path('', HomePageView.as_view(), name='home'),

    path('features/', FeaturesView.as_view(), name='features'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)