# ai_recruitment_platform/candidates/urls.py

from django.urls import path
from . import views

app_name = 'candidates' # Namespace for candidate URLs

urlpatterns = [
    # View the logged-in candidate's profile
    path('profile/', views.CandidateProfileView.as_view(), name='candidate_profile'),
    # Upload a new resume (requires login and candidate role)
    path('profile/upload-resume/', views.CandidateResumeUploadView.as_view(), name='resume_upload'),

    # Future: edit profile, view applications as candidate, etc.
]