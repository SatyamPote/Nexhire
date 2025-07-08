# ai_recruitment_platform/candidates/models.py

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
# Import UserProfile from the users app
from users.models import UserProfile, PARSE_STATUS_CHOICES # Assuming PARSE_STATUS_CHOICES is defined here

# Re-define PARSE_STATUS_CHOICES here if you haven't imported it from users.models
# This ensures the model is self-contained if UserProfile isn't directly linked yet.
# For now, we'll import it. If you get an ImportError, uncomment the next lines
# and comment out the import.
# PARSE_STATUS_CHOICES = [
#     ('pending', 'Pending'),
#     ('parsing', 'Parsing'),
#     ('success', 'Success'),
#     ('failed', 'Failed'),
# ]

class Candidate(models.Model):
    """
    Represents a candidate profile, linked one-to-one with a UserProfile.
    This model holds data specifically relevant to a candidate's interaction with the platform.
    """
    # A Candidate *is* a UserProfile that's acting as a candidate.
    # Using OneToOneField with primary_key=True means a Candidate object is also the primary key.
    # This is a common way to ensure a UserProfile can only be a Candidate once.
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='candidate_profile', # Access candidate data from UserProfile: user_profile.candidate_profile
        primary_key=True, # This model's primary key is the UserProfile's ID
        verbose_name='User Profile'
    )
    # You can add candidate-specific fields here.
    # For now, we'll keep it simple and rely on UserProfile for basic contact info.
    # If a candidate needs a DIFFERENT phone number than their main profile phone, add it here.
    # phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Candidate's contact phone number.")

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
    Stores resume files uploaded by candidates and tracks their parsing status.
    """
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='resumes', # Access resumes from a candidate: candidate.resumes.all()
        help_text="The candidate to whom this resume belongs."
    )
    # FileField handles storing files. 'upload_to' specifies a subdirectory within MEDIA_ROOT.
    resume_file = models.FileField(
        upload_to='resumes/',
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
    # Future fields: resume_score, keywords, etc.

    def __str__(self):
        # Display the candidate's name and upload date
        return f"Resume for {self.candidate} ({self.uploaded_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = 'Candidate Resume'
        verbose_name_plural = 'Candidate Resumes'
        ordering = ['-uploaded_at'] # Show the most recent resume first

# --- Admin configuration for Candidate and Resume ---
# File Path: ai_recruitment_platform/candidates/admin.py

from django.contrib import admin
from .models import Candidate, Resume
# Import the form we'll create next to handle UserProfile linkage
from .forms import CandidateForm # Assuming you'll create this file

# Define an Inline for Resumes to be displayed when editing a Candidate
class ResumeInline(admin.TabularInline):
    model = Resume
    extra = 1 # Show one blank form for adding new resumes by default
    # Initially, these fields are not directly editable via the inline
    readonly_fields = ('uploaded_at', 'parse_status')
    # We'll manage parse_status and parsed_data via signals/tasks later

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    # Use the custom form to ensure proper UserProfile linkage
    form = CandidateForm
    # Display related UserProfile information directly in the list_display
    list_display = ('full_name', 'email', 'phone', 'linkedin_profile', 'github_profile', 'num_resumes', 'created_at')
    list_filter = ('created_at', 'user_profile__role') # Filter by creation date and user's role
    search_fields = (
        'user_profile__user__first_name',
        'user_profile__user__last_name',
        'user_profile__user__username',
        'user_profile__user__email',
        'linkedin_profile_url',
        'github_profile_url'
    )
    inlines = [ResumeInline] # Add the ResumeInline
    # Make the linked UserProfile read-only, as it's managed by the form and signals.
    readonly_fields = ('user_profile', 'created_at', 'updated_at')

    # Helper methods to display related data in list_display
    def full_name(self, obj):
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.user_profile.user.email
    email.short_description = 'Email'

    def phone(self, obj):
        # Try to get phone from candidate profile, then fall back to user profile
        return obj.phone_number or obj.user_profile.phone_number
    phone.short_description = 'Phone'

    def linkedin_profile(self, obj):
        return obj.linkedin_profile_url
    linkedin_profile.short_description = 'LinkedIn'

    def github_profile(self, obj):
        return obj.github_profile_url
    github_profile.short_description = 'GitHub'

    def num_resumes(self, obj):
        return obj.resumes.count()
    num_resumes.short_description = 'Resumes'

    # When adding a new candidate, the 'user_profile' field is handled by the form.
    # We don't need to override save_model here unless we want custom logic.

# --- Custom Form for Candidate ---
# This is crucial for ensuring that a Candidate is linked to a valid,
# available UserProfile.
# File Path: ai_recruitment_platform/candidates/forms.py

from django import forms
from .models import Candidate, UserProfile # Import UserProfile directly
from django.contrib.auth import get_user_model # Safest way to get the User model

User = get_user_model()

class CandidateForm(forms.ModelForm):
    # Add fields from the Candidate model that we want to be editable in the admin form.
    # UserProfile is handled separately.
    class Meta:
        model = Candidate
        fields = ['linkedin_profile_url', 'github_profile_url', 'portfolio_url']
        # Exclude 'user_profile' as we will handle its selection/creation in __init__
        # exclude = ['user_profile'] # Alternative to listing fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set the queryset for the user_profile field.
        # We only want to allow linking to UserProfile instances that:
        # 1. Do not already have a Candidate profile associated with them.
        # 2. Have the 'candidate' role assigned.
        self.fields['user_profile'] = forms.ModelChoiceField(
            queryset=UserProfile.objects.filter(
                candidate_profile__isnull=True, # Ensure this UserProfile isn't already a Candidate
                role='candidate' # Ensure this UserProfile has the 'candidate' role
            ),
            label="User Account",
            help_text="Select the user account that will represent this candidate."
        )

    # Override clean method to add validation logic for the user_profile field
    def clean_user_profile(self):
        user_profile = self.cleaned_data.get('user_profile')
        # The queryset in __init__ already filters out existing candidates and wrong roles.
        # So, this validation is mostly a safeguard.
        if user_profile and Candidate.objects.filter(user_profile=user_profile).exists():
            # This should theoretically not happen due to the queryset filter, but good to have.
            raise forms.ValidationError("This user account is already associated with a candidate profile.")
        return user_profile