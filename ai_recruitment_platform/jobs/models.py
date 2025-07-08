# ai_recruitment_platform/jobs/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone # For default published_date

# Define choices for job status
JOB_STATUS_CHOICES = [
    ('open', 'Open'),
    ('closed', 'Closed'),
    ('draft', 'Draft'),
    ('on_hold', 'On Hold'),
]

class Job(models.Model):
    """
    Represents a job posting within the recruitment platform.
    """
    title = models.CharField(max_length=255, help_text="The title of the job position.")
    description = models.TextField(help_text="A detailed description of the job role and responsibilities.")
    responsibilities = models.TextField(blank=True, null=True, help_text="Key responsibilities of the role.")
    requirements = models.TextField(blank=True, null=True, help_text="Required qualifications and skills.")
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Job location (e.g., City, Country).")
    employment_type = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Type of employment (e.g., Full-time, Part-time, Contract)."
    )
    salary_range = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Salary range for the position (e.g., '$50,000 - $70,000')."
    )
    # Link to the user who posted the job.
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If the user is deleted, don't delete the job
        null=True, # Allow the job to exist without a poster for a while if needed
        related_name='jobs_posted', # Access jobs from a user: user.jobs_posted.all()
        help_text="The user who posted this job."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(
        default=timezone.now, # Default to now if not specified
        help_text="Date and time the job was made public."
    )
    status = models.CharField(
        max_length=10,
        choices=JOB_STATUS_CHOICES,
        default='draft', # Default to draft, requires explicit publish
        help_text="Current status of the job posting."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether the job posting is visible to candidates."
    )

    def __str__(self):
        # Return the job title and its current status
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Job Posting'
        verbose_name_plural = 'Job Postings'
        ordering = ['-published_date', 'title'] # Order by publish date (newest first), then title

# --- Admin configuration for Job ---
# File Path: ai_recruitment_platform/jobs/admin.py

from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'employment_type', 'status', 'posted_by', 'published_date', 'is_active')
    list_filter = ('status', 'location', 'employment_type', 'is_active', 'published_date')
    search_fields = ('title', 'description', 'location', 'posted_by__username', 'posted_by__email') # Search by job details and poster
    readonly_fields = ('created_at', 'updated_at', 'published_date') # These are managed automatically
    # Make 'description' prepopulated from 'title' if desired for simpler fields, but description is usually unique.
    # prepopulated_fields = {'description': ('title',)} # This is more for slug fields, not text fields.

    # Add an autocomplete dropdown for 'posted_by' for better usability with many users
    autocomplete_fields = ('posted_by',)