# ai_recruitment_platform/jobs/forms.py

from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    """
    Form for creating and editing Job postings.
    """
    class Meta:
        model = Job
        # Fields to be included in the form. 'posted_by' is handled by the view.
        fields = [
            'title',
            'description',
            'responsibilities',
            'requirements',
            'location',
            'employment_type',
            'salary_range',
            'status', # Allow status to be set on creation/edit
            'is_active',
        ]
        # Optionally exclude fields that are managed automatically or not needed in the form
        # exclude = ['posted_by', 'created_at', 'updated_at', 'published_date']

        # Customizing widgets for better UX
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Job Title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Detailed job description...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Key responsibilities...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Required qualifications...'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Remote, New York, USA'}),
            'employment_type': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Full-time, Contract'}),
            'salary_range': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., $60,000 - $80,000'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }