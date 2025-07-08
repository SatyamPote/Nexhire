# ai_recruitment_platform/jobs/urls.py

from django.urls import path
from . import views

app_name = 'jobs' # Namespace for job URLs

urlpatterns = [
    # List all open jobs
    path('', views.JobListView.as_view(), name='job_list'),
    # View a single job (e.g., /jobs/1/)
    path('<int:job_id>/', views.JobDetailView.as_view(), name='job_detail'),
    # Create a new job posting (requires login and recruiter role)
    path('new/', views.JobCreateView.as_view(), name='job_create'),

    # Future: update job, delete job, etc.
]