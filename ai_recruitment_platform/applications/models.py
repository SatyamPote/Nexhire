# ai_recruitment_platform/applications/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

# Define choices for application status
APPLICATION_STATUS_CHOICES = [
    ('applied', 'Applied'),
    ('screening', 'Screening'),
    ('interviewing', 'Interviewing'),
    ('assessment', 'Assessment'),
    ('offer', 'Offer Extended'),
    ('rejected', 'Rejected'),
    ('hired', 'Hired'),
    ('withdrawn', 'Withdrawn'),
]

class Application(models.Model):
    """
    Represents a candidate's application to a specific job.
    This acts as a bridge table between Candidate and Job.
    """
    # Use string references for ForeignKey to avoid circular imports
    # if apps are created in a different order.
    candidate = models.ForeignKey(
        'candidates.Candidate',
        on_delete=models.CASCADE,
        related_name='applications', # Access applications from a candidate: candidate.applications.all()
        help_text="The candidate applying for the job."
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.CASCADE,
        related_name='applications', # Access applications for a job: job.applications.all()
        help_text="The job being applied for."
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the application was submitted."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of the last update to the application."
    )
    status = models.CharField(
        max_length=20,
        choices=APPLICATION_STATUS_CHOICES,
        default='applied', # Default status upon submission
        help_text="Current status of the application in the hiring process."
    )

    # --- Fields for AI Integration (to be populated later) ---
    resume_score = models.FloatField(
        blank=True, null=True,
        help_text="AI-generated score indicating resume match quality."
    )
    interview_score = models.FloatField(
        blank=True, null=True,
        help_text="AI-generated score from interviews."
    )
    feedback_notes = models.TextField(
        blank=True, null=True,
        help_text="Recruiter or AI feedback on the application."
    )

    def __str__(self):
        # Clear and informative string representation
        return f"Application: {self.candidate} for {self.job.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Job Application'
        verbose_name_plural = 'Job Applications'
        ordering = ['-applied_at']
        # Ensure a candidate cannot apply for the same job more than once
        unique_together = ('candidate', 'job')

# --- Admin configuration for Application ---
# File Path: ai_recruitment_platform/applications/admin.py

from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('candidate_full_name', 'job_title', 'status', 'applied_at', 'resume_score', 'interview_score')
    list_filter = ('status', 'applied_at', 'resume_score', 'interview_score')
    search_fields = (
        'candidate__user_profile__user__first_name',
        'candidate__user_profile__user__last_name',
        'candidate__user_profile__user__username',
        'candidate__user_profile__user__email',
        'job__title',
        'job__location',
    )
    # Make core fields read-only, as they are determined by the application itself
    readonly_fields = ('candidate', 'job', 'applied_at', 'updated_at')
    # Allow editing of status, scores, and notes
    list_editable = ('status', 'resume_score', 'interview_score')

    # Custom methods to display more informative data in list_display
    def candidate_full_name(self, obj):
        return obj.candidate.user_profile.user.get_full_name() or obj.candidate.user_profile.user.username
    candidate_full_name.short_description = 'Candidate'

    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job Title'