# ai_recruitment_platform/jobs/urls.py

from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:job_id>/', views.JobDetailView.as_view(), name='job_detail'),
    path('new/', views.JobCreateView.as_view(), name='job_create'),
    # Job Management URLs
    path('<int:job_id>/edit/', views.JobUpdateView.as_view(), name='job_edit'),
    path('<int:job_id>/delete/', views.JobDeleteView.as_view(), name='job_delete'),
    # Recruiter Specific URLs
    path('my-applications/', views.RecruiterJobApplicationsView.as_view(), name='recruiter_applications'),
    # AI Review URL for Applications
    path('review/application/<int:application_id>/', views.ResumeAIReviewView.as_view(), name='review_application_ai'),
]