# ai_recruitment_platform/users/urls.py

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.CandidateProfileView.as_view(), name='candidate_profile'),
    path('profile/upload-resume/', views.CandidateResumeUploadView.as_view(), name='resume_upload'),
    path('<int:pk>/', views.CandidateDetailView.as_view(), name='candidate_detail'),
    
    # --- Role Selection URL ---
    path('select-role/', views.RoleSelectionView.as_view(), name='role_selection'),
]