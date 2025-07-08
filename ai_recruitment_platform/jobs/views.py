# ai_recruitment_platform/jobs/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # For authentication and role checking

from .models import Job
from .forms import JobForm # We'll create this form next

class JobListView(View):
    """
    Displays a list of active job postings.
    """
    template_name = 'jobs/job_list.html' # Will create this template later

    def get(self, request, *args, **kwargs):
        # Filter for active and open jobs for candidates to see
        jobs = Job.objects.filter(is_active=True, status='open').order_by('-published_date')
        context = {'jobs': jobs}
        return render(request, self.template_name, context)

class JobDetailView(View):
    """
    Displays the details of a single job posting.
    """
    template_name = 'jobs/job_detail.html' # Will create this template later

    def get(self, request, job_id, *args, **kwargs):
        # Get the job object or return a 404 if not found
        job = get_object_or_404(Job, pk=job_id)
        context = {'job': job}
        return render(request, self.template_name, context)

class JobCreateView(LoginRequiredMixin, View): # Requires login
    """
    Allows logged-in users (specifically recruiters) to create new job postings.
    """
    template_name = 'jobs/job_create.html' # Will create this template later
    form_class = JobForm
    success_url = reverse_lazy('jobs:job_list') # Redirect to job list after successful creation

    # Test if the user is a recruiter
    def test_func(self):
        # self.request.user is available here
        # We need to ensure UserProfile and its 'role' field exist for the logged-in user
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role == 'recruiter'
        return False # If no profile, or no role, they can't create jobs

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            # Assign the currently logged-in user as the poster
            job.posted_by = request.user
            job.save()
            # You might want to automatically set status to 'draft' or 'open' on creation
            # For now, it defaults to 'draft' from the model.
            return redirect(self.success_url)
        else:
            # If form is invalid, re-render the form with errors
            context = {'form': form}
            return render(request, self.template_name, context)

# We'll add JobUpdateView and JobDeleteView later for a full CRUD