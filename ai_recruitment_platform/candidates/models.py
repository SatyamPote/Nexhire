# ai_recruitment_platform/candidates/models.py

from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
# Remove the import from users.models as PARSE_STATUS_CHOICES will be defined here.
# from users.models import UserProfile, PARSE_STATUS_CHOICES # This caused the error

# Import UserProfile from the users app directly
from users.models import UserProfile


# Define choices for resume parsing status locally, as it's used only in this model
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
    user_profile = models.OneToOneField(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='candidate_profile',
        primary_key=True,
        verbose_name='User Account'
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
        related_name='resumes',
        help_text="The candidate to whom this resume belongs."
    )
    resume_file = models.FileField(
        upload_to='resumes/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'rtf'])
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

    def __str__(self):
        return f"Resume for {self.candidate} ({self.uploaded_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = 'Candidate Resume'
        verbose_name_plural = 'Candidate Resumes'
        ordering = ['-uploaded_at']

# --- Admin configuration for Candidate and Resume ---
# File Path: ai_recruitment_platform/candidates/admin.py

from django.contrib import admin
from .models import Candidate, Resume
from .forms import CandidateForm # Assuming you'll create this file

class ResumeInline(admin.TabularInline):
    model = Resume
    extra = 1
    readonly_fields = ('uploaded_at', 'parse_status')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ('full_name', 'email', 'phone', 'linkedin_profile', 'github_profile', 'num_resumes', 'created_at')
    list_filter = ('created_at', 'user_profile__role')
    search_fields = (
        'user_profile__user__first_name',
        'user_profile__user__last_name',
        'user_profile__user__username',
        'user_profile__user__email',
        'linkedin_profile_url',
        'github_profile_url'
    )
    inlines = [ResumeInline]
    readonly_fields = ('user_profile', 'created_at', 'updated_at')

    def full_name(self, obj):
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.user_profile.user.email
    email.short_description = 'Email'

    def phone(self, obj):
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

# --- Custom Form for Candidate ---
# File Path: ai_recruitment_platform/candidates/forms.py

from django import forms
from .models import Candidate, UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['linkedin_profile_url', 'github_profile_url', 'portfolio_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_profile'] = forms.ModelChoiceField(
            queryset=UserProfile.objects.filter(
                candidate_profile__isnull=True,
                role='candidate'
            ),
            label="User Account",
            help_text="Select the user account that will represent this candidate."
        )

    def clean_user_profile(self):
        user_profile = self.cleaned_data.get('user_profile')
        if user_profile and Candidate.objects.filter(user_profile=user_profile).exists():
            raise forms.ValidationError("This user account is already associated with a candidate profile.")
        return user_profile