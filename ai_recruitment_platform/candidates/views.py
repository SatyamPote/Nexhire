# ai_recruitment_platform/candidates/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Candidate, Resume
from .forms import CandidateForm, ResumeForm # Create ResumeForm next

class CandidateProfileView(LoginRequiredMixin, View):
    """
    Displays the current logged-in candidate's profile and uploaded resumes.
    """
    template_name = 'candidates/candidate_profile.html' # Will create this

    def get(self, request, *args, **kwargs):
        # Try to get the candidate profile for the logged-in user
        try:
            candidate = request.user.profile.candidate_profile # Access via UserProfile -> candidate_profile
            # Ensure the linked UserProfile indeed has the 'candidate' role
            if request.user.profile.role != 'candidate':
                # Redirect or show an error if user is not a candidate
                # For now, let's redirect to a generic unauthorized page or homepage
                return redirect('home') # Assuming you have a 'home' URL name
        except AttributeError:
            # If the user doesn't have a candidate profile linked or is not a candidate user
            # Redirect to create profile or a relevant page
            return redirect('home') # Or a page to onboard as a candidate

        context = {'candidate': candidate}
        return render(request, self.template_name, context)

class CandidateResumeUploadView(LoginRequiredMixin, View):
    """
    Allows a logged-in candidate to upload a new resume.
    """
    template_name = 'candidates/resume_upload.html' # Will create this
    form_class = ResumeForm
    success_url = reverse_lazy('candidates:candidate_profile') # Redirect to profile after upload

    # Test if the user is a candidate
    def test_func(self):
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'candidate'
        return False

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES) # Handle POST data and file uploads
        if form.is_valid():
            resume = form.save(commit=False)
            try:
                # Get the current candidate profile
                resume.candidate = request.user.profile.candidate_profile
                resume.save()
                # Trigger resume parsing (this will be a background task later)
                # For now, it just saves with 'pending' status.
                return redirect(self.success_url)
            except AttributeError:
                # User is not a candidate or doesn't have a profile linked.
                # This should be caught by test_func, but as a safeguard.
                return redirect('home')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)