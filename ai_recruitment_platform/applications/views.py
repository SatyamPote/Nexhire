# ai_recruitment_platform/applications/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

from jobs.models import Job
from .models import Application
from candidates.models import Resume

class ApplyJobView(LoginRequiredMixin, UserPassesTestMixin, View):
    # ... (existing ApplyJobView code) ...
    login_url = 'home'
    def test_func(self):
        if not hasattr(self.request.user, 'profile') or self.request.user.profile.role != 'candidate':
            return False
        try:
            candidate_profile = self.request.user.profile.candidate_profile
            if not candidate_profile or not candidate_profile.resumes.exists():
                return False
            return True
        except AttributeError:
            return False

    def post(self, request, job_id, *args, **kwargs):
        job = get_object_or_404(Job, pk=job_id)
        try:
            candidate = request.user.profile.candidate_profile
            if Application.objects.filter(candidate=candidate, job=job).exists():
                messages.warning(request, "You have already applied for this job.")
                return redirect('jobs:job_list')

            Application.objects.create(candidate=candidate, job=job, status='applied')
            messages.success(request, f"Successfully applied for '{job.title}'.")
            return redirect('jobs:job_list')

        except AttributeError:
            messages.error(request, "You must be a logged-in candidate with a profile and resume to apply.")
            return redirect('candidates:candidate_profile')

class ApplicationDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'applications/application_detail.html'
    model = Application

    def test_func(self):
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['recruiter', 'admin']
        return False

    def get(self, request, pk, *args, **kwargs):
        try:
            app = self.model.objects.get(pk=pk)
            if request.user.profile.role == 'recruiter' and request.user != app.job.posted_by:
                messages.error(request, "You do not have permission to view this application.")
                return redirect('jobs:recruiter_applications')
            
            context = {'application': app}
            return render(request, self.template_name, context)
        except self.model.DoesNotExist:
            messages.error(request, "Application not found.")
            return redirect('jobs:recruiter_applications')
        except PermissionError:
            messages.error(request, "You do not have permission to view this application.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

# --- New View: ApplicationUpdateStatusView ---
class ApplicationUpdateStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Allows recruiters to update the status of an application.
    """
    template_name = 'applications/application_update_status.html' # A simple form page
    model = Application

    def test_func(self):
        # Recruiters and admins can update statuses
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['recruiter', 'admin']
        return False

    def get_object(self, pk):
        """Helper to get application and check recruiter ownership."""
        app = get_object_or_404(self.model, pk=pk)
        # Ensure the logged-in user is the recruiter who posted the job, or an admin
        if self.request.user.profile.role == 'recruiter' and self.request.user != app.job.posted_by:
            raise PermissionError("You do not have permission to update this application's status.")
        return app

    def get(self, request, pk, *args, **kwargs):
        """Displays the form to update the status."""
        try:
            app = self.get_object(pk)
            
            # This form will be simple: a dropdown for status
            # We use Django's ModelForm for convenience
            from .forms import ApplicationStatusForm # We'll define this form next
            form = ApplicationStatusForm(instance=app)
            
            context = {'application': app, 'form': form}
            return render(request, self.template_name, context)

        except PermissionError:
            messages.error(request, "You do not have permission to update this application.")
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

    def post(self, request, pk, *args, **kwargs):
        """Handles the status update submission."""
        try:
            app = self.get_object(pk)
            
            from .forms import ApplicationStatusForm # Import form again if needed here
            form = ApplicationStatusForm(request.POST, instance=app)

            if form.is_valid():
                form.save()
                messages.success(request, f"Application status updated to '{app.get_status_display()}'.")
                return redirect('jobs:recruiter_applications') # Redirect back to the list
            else:
                # If form is invalid, re-render with errors
                context = {'application': app, 'form': form}
                return render(request, self.template_name, context)

        except PermissionError:
            messages.error(request, "You do not have permission to update this application.")
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')