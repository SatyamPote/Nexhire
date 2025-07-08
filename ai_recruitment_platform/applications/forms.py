# ai_recruitment_platform/applications/forms.py

from django import forms
from .models import Application

class ApplicationStatusForm(forms.ModelForm):
    """
    Form to update the status of a job application.
    """
    class Meta:
        model = Application
        fields = ['status'] # Only the status field will be editable
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}) # Use Tailwind styling
        }

    # You can add custom clean methods here if needed, but for status update,
    # it's usually straightforward.