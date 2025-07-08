# ai_recruitment_platform/candidates/forms.py

# <<< ADD THIS IMPORT >>>
from django import forms
# <<< END ADDITION >>>

from .models import Candidate, UserProfile # Import UserProfile directly
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


# --- Add the ResumeForm definition here ---
# Import Resume model for the form
from .models import Resume

class ResumeForm(forms.ModelForm):
    """
    Form for uploading a candidate's resume.
    """
    class Meta:
        model = Resume
        fields = ['resume_file'] # Only the file upload field is needed here

    widgets = {
        'resume_file': forms.ClearableFileInput(attrs={'class': 'form-file-input'}),
    }