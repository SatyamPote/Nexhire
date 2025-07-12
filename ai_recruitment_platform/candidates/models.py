# ai_recruitment_platform/candidates/models.py

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
# Import UserProfile from the users app
from users.models import UserProfile # Ensure this import is correct

# Define choices for resume parsing status
PARSE_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('parsing', 'Parsing'),
    ('success', 'Success'),
    ('failed', 'Failed'),
]

class Candidate(models.Model):
    """
    Represents a candidate profile, linked one-to-one with a UserProfile.
    This model holds data specifically relevant to a candidate's interaction with the platform.
    """
    # A Candidate *is* a UserProfile that's acting as a candidate.
    # Using OneToOneField with primary_key=True means a Candidate object is also the primary key.
    user_profile = models.OneToOneField(
        UserProfile, # Links Candidate to UserProfile
        on_delete=models.CASCADE,
        related_name='candidate_profile',
        primary_key=True, # This model's primary key is the UserProfile's ID
        verbose_name='User Profile'
    )
    linkedin_profile_url = models.URLField(
        blank=True, null=True,
        help_text="URL to the candidate's LinkedIn profile."
    )
    github_profile_url = models.URLField(
        blank=True, null=True,
        help_text="URL to the candidate's GitHub profile."
    )
    portfolio_url = models.URLField(
        blank=True, null=True,
        help_text="URL to the candidate's personal portfolio or website."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Display the full name or username from the linked UserProfile
        return f"Candidate: {self.user_profile.user.get_full_name() or self.user_profile.user.username}"

    class Meta:
        verbose_name = 'Candidate Profile'
        verbose_name_plural = 'Candidate Profiles'

class Resume(models.Model):
    """
    Stores resume files uploaded by candidates and tracks their parsing status,
    plus AI-generated scores and feedback.
    """
    candidate = models.ForeignKey(
        Candidate, # Links Resume to Candidate
        on_delete=models.CASCADE,
        related_name='resumes', # Access resumes from a candidate: candidate.resumes.all()
        help_text="The candidate to whom this resume belongs."
    )
    resume_file = models.FileField(
        upload_to='resumes/', # This will create a 'resumes' directory within your MEDIA_ROOT
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'rtf']) # Add more if needed
        ],
        help_text="The resume file uploaded by the candidate."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parse_status = models.CharField(
        max_length=10,
        choices=PARSE_STATUS_CHOICES,
        default='pending',
        help_text="Status of the resume parsing process."
    )
    parsed_data = models.JSONField(
        blank=True, null=True,
        help_text="Structured data extracted from the resume by the parsing service."
    )

    # --- AI Screening Fields ---
    ai_resume_score = models.FloatField(
        blank=True, null=True,
        help_text="AI-generated score indicating resume match quality against a job."
    )
    ai_feedback = models.TextField(
        blank=True, null=True,
        help_text="AI-generated feedback on the resume's strengths and weaknesses."
    )

    def __str__(self):
        return f"Resume for {self.candidate} ({self.uploaded_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = 'Candidate Resume'
        verbose_name_plural = 'Candidate Resumes'
        ordering = ['-uploaded_at']