# ai_recruitment_platform/applications/urls.py

from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_id>/', views.ApplyJobView.as_view(), name='apply_job'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    # --- New URL for Updating Application Status ---
    path('<int:pk>/update-status/', views.ApplicationUpdateStatusView.as_view(), name='application_update_status'),
]