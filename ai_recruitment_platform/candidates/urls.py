# ai_recruitment_platform/candidates/urls.py

from django.urls import path
from . import views

app_name = 'candidates'

urlpatterns = [
    path('profile/', views.CandidateProfileView.as_view(), name='candidate_profile'),
    path('profile/upload-resume/', views.CandidateResumeUploadView.as_view(), name='resume_upload'),
    # --- URL for Candidate Detail View ---
    # It expects a primary key (pk) for the candidate.
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='candidate_detail'),
]