# ai_recruitment_platform/users/forms.py

from django import forms
from .models import UserProfile # Import UserProfile model

# --- CandidateForm and ResumeForm (from previous steps) ---
# Ensure these are present if they are defined in this file.

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['linkedin_profile_url', 'github_profile_url', 'portfolio_url']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_profile'] = forms.ModelChoiceField(
            queryset=UserProfile.objects.filter(candidate_profile__isnull=True, role='candidate'),
            label="User Account",
            help_text="Select the user account for this candidate."
        )

    def clean_user_profile(self):
        user_profile = self.cleaned_data.get('user_profile')
        if user_profile and Candidate.objects.filter(user_profile=user_profile).exists():
            raise forms.ValidationError("This user is already a candidate.")
        return user_profile

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['resume_file']
    widgets = {'resume_file': forms.ClearableFileInput(attrs={'class': 'form-file-input'})}

# --- New Form: RoleForm ---
class RoleForm(forms.ModelForm):
    """
    Form for selecting a user role (Candidate/Recruiter).
    """
    class Meta:
        model = UserProfile
        fields = ['role'] # Only the role field will be editable via this form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Customize widget for role selection if needed
        # For example, make it a nicer select input.
        self.fields['role'].widget.attrs.update({
            'class': 'form-select',
            'label': 'Select your role'
        })
        # Filter out the admin role if you don't want regular users to select it
        # Or ensure only specific users can select certain roles.
        # For now, let's allow selection of candidate/recruiter.