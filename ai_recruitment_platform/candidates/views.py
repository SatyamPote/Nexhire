# ai_recruitment_platform/candidates/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages

from .models import Candidate, Resume
from .forms import CandidateForm, ResumeForm
# Import UserProfile for the CandidateDetailView if needed for context,
# but Candidate model already links to it.

class CandidateProfileView(LoginRequiredMixin, View):
    template_name = 'candidates/candidate_profile.html'

    def get(self, request, *args, **kwargs):
        try:
            candidate = request.user.profile.candidate_profile
            if request.user.profile.role != 'candidate':
                messages.error(request, "You are not registered as a candidate.")
                return redirect('home')
        except AttributeError:
            messages.error(request, "You need to complete your candidate profile.")
            return redirect('home')

        context = {'candidate': candidate}
        return render(request, self.template_name, context)

class CandidateResumeUploadView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'candidates/resume_upload.html'
    form_class = ResumeForm
    success_url = reverse_lazy('candidates:candidate_profile')

    def test_func(self):
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'candidate'
        return False

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            try:
                resume.candidate = request.user.profile.candidate_profile
                resume.save()
                messages.success(request, "Resume uploaded successfully.")
                return redirect(self.success_url)
            except AttributeError:
                messages.error(request, "You are not registered as a candidate or your profile is incomplete.")
                return redirect('home')
        else:
            context = {'form': form}
            return render(request, self.template_name, context)

class CandidateDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Displays a candidate's profile details, intended for recruiter use.
    """
    template_name = 'candidates/candidate_detail.html'
    model = Candidate # The model we are displaying details for

    def test_func(self):
        """
        Checks if the logged-in user is a recruiter or admin.
        """
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['recruiter', 'admin']
        return False

    def get(self, request, pk, *args, **kwargs):
        """
        Retrieves and displays the candidate's profile.
        'pk' here refers to the primary key of the Candidate object,
        which is also the UserProfile's pk due to OneToOneField(primary_key=True).
        """
        try:
            # Fetch the Candidate object using the primary key
            candidate = self.model.objects.get(pk=pk)
            context = {'candidate': candidate}
            return render(request, self.template_name, context)
        except self.model.DoesNotExist:
            messages.error(request, "Candidate profile not found.")
            # Redirect to a page where recruiters can see job applications
            return redirect('jobs:recruiter_applications')
        except PermissionError:
            # This exception would be raised by test_func if it failed,
            # but we handle it here for robustness.
            messages.error(request, "You do not have permission to view this candidate.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')