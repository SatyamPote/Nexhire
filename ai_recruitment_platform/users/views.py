# ai_recruitment_platform/users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth import login as django_login # To log in Django users
from django.contrib.auth import get_user_model
from candidates.models import Candidate
from .models import UserProfile, Candidate # Import UserProfile and Candidate
from jobs.models import Job
from applications.models import Application
from .forms import CandidateForm, ResumeForm, RoleForm # Import RoleForm

# --- Placeholder for AI Screening Logic ---
# ... (perform_ai_screening, parse_resume_with_api functions) ...

# --- Existing Views ---
# (JobListView, JobDetailView, JobCreateView, JobUpdateView, JobDeleteView, RecruiterJobApplicationsView, ResumeAIReviewView)
# ... paste your existing Job views here ...

# --- Candidate Views ---
class CandidateProfileView(LoginRequiredMixin, View):
    # ... (paste existing CandidateProfileView) ...
    pass
class CandidateResumeUploadView(LoginRequiredMixin, UserPassesTestMixin, View):
    # ... (paste existing CandidateResumeUploadView) ...
    pass
class CandidateDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'candidates/candidate_detail.html'
    model = Candidate

    def test_func(self):
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.role in ['recruiter', 'admin']
        return False

    def get(self, request, pk, *args, **kwargs):
        try:
            candidate = self.model.objects.get(pk=pk)
            # Pass the role to template if needed for conditional rendering
            context = {'candidate': candidate}
            return render(request, self.template_name, context)
        except self.model.DoesNotExist:
            messages.error(request, "Candidate profile not found.")
            return redirect('jobs:recruiter_applications')
        except PermissionError:
            messages.error(request, "You do not have permission to view this candidate.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')


# --- New View: Role Selection View ---
class RoleSelectionView(LoginRequiredMixin, View):
    """
    View to prompt the user to select their role after initial signup
    if their role is not yet explicitly determined.
    """
    template_name = 'users/role_selection.html' # Template for role selection form
    form_class = RoleForm # Use the RoleForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login') # Must be logged in to select role

        try:
            user_profile = request.user.profile
            # If role is already explicitly set (e.g., not default candidate), or setup is done, redirect.
            # The 'role_selection_completed' flag is ideal here.
            if user_profile.role_selection_completed:
                # If role selection is done, redirect to appropriate dashboard
                if user_profile.role == 'recruiter':
                    return redirect('jobs:recruiter_applications')
                else: # Candidate or any other role
                    return redirect('candidates:candidate_profile')

            # If role is unset or still the default 'candidate' that needs confirmation
            # Show the role selection form.
            form = self.form_class(instance=user_profile) # Pre-fill with existing profile if any
            context = {'form': form, 'user_profile': user_profile}
            return render(request, self.template_name, context)
        
        except UserProfile.DoesNotExist:
            # This should ideally not happen if signals are working correctly.
            messages.error(request, "UserProfile not found. Please contact support.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('home')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')

        try:
            user_profile = request.user.profile
            form = self.form_class(request.POST, instance=user_profile) # Pass instance to update

            if form.is_valid():
                form.save() # Saves the selected role
                # Mark role selection as completed
                user_profile.role_selection_completed = True
                user_profile.save()
                
                messages.success(request, "Your role has been set successfully!")

                # --- Redirect based on selected role ---
                if user_profile.role == 'recruiter':
                    return redirect('jobs:recruiter_applications') # Redirect to recruiter dashboard
                elif user_profile.role == 'candidate':
                    return redirect('candidates:candidate_profile') # Redirect to candidate profile
                else: # Should not happen if role choices are enforced
                    return redirect('home') # Fallback redirect
            else:
                # If form is invalid, re-render with errors
                context = {'form': form, 'user_profile': user_profile}
                return render(request, self.template_name, context)

        except UserProfile.DoesNotExist:
            messages.error(request, "UserProfile not found. Please contact support.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('home')