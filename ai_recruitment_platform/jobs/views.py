# ai_recruitment_platform/jobs/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Job
from .forms import JobForm
from applications.models import Application
from candidates.models import Resume # Import Resume model for screening

# --- Helper Functions for Resume Parsing and AI Screening ---

def parse_resume_with_api(resume_file):
    """
    Simulates calling an external resume parsing API.
    In a real scenario, this would make an HTTP request to Affinda/Sovren etc.
    It should return a dictionary of parsed data.
    """
    if not resume_file:
        return None

    # Ensure the file pointer is at the beginning
    resume_file.seek(0)
    
    # --- SIMULATION ---
    # Simulate parsing by returning dummy data based on file content
    try:
        resume_text = resume_file.read().decode('utf-8', errors='ignore')
        # Basic simulation: extract first few words as a fake skill
        words = resume_text.split()
        fake_skills = " ".join(words[:5]) if words else "Simulated Skill"
        parsed_data = {
            "skills": [fake_skills],
            "job_title": "Simulated Job Title",
            "company": "Simulated Company",
            "education": "Simulated Degree",
            "years_experience": len(words) / 100 # Dummy calculation
        }
        return parsed_data
    except Exception as e:
        print(f"Error simulating resume parsing: {e}") # Log error
        return None
    # --- END SIMULATION ---

def perform_ai_screening(parsed_resume_data, job_description):
    """
    Simulates AI scoring based on parsed resume data and job description.
    In a real scenario:
    1. Use OpenAI GPT-4 or similar.
    2. Prompt the AI with parsed_resume_data and job_description.
    3. Return a score and feedback.
    """
    score = 0.0
    feedback = "AI analysis is pending."

    if parsed_resume_data and job_description:
        # Simulate scoring based on presence of certain keys and job description length
        score_factors = 0
        if parsed_resume_data.get("years_experience", 0) > 3: score_factors += 20
        # Check for 'Simulated Skill' in the list of skills
        if "Simulated Skill" in parsed_resume_data.get("skills", []): score_factors += 30
        if len(job_description.split()) > 50: score_factors += 20
        if parsed_resume_data.get("education") == "Simulated Degree": score_factors += 10

        score = min(100.0, float(score_factors)) # Cap score at 100
        feedback = f"AI Score: {score:.2f}. "

        if score > 85: feedback += "Very strong match. "
        elif score > 60: feedback += "Good match. "
        else: feedback += "Potential match, requires review. "

        # Add some general feedback based on simulated data
        feedback += f"Simulated experience: {parsed_resume_data.get('years_experience', 'N/A')} years. Key skills identified: {', '.join(parsed_resume_data.get('skills', ['None']))}."

    else:
        score = 0.0
        feedback = "Could not perform screening due to missing parsed data or job description."

    return score, feedback
# --- End Helper Functions ---


# --- View Classes ---
class JobListView(View):
    template_name = 'jobs/job_list.html'

    def get(self, request, *args, **kwargs):
        jobs = Job.objects.filter(is_active=True, status='open').order_by('-published_date')
        context = {'jobs': jobs}
        return render(request, self.template_name, context)

class JobDetailView(View):
    template_name = 'jobs/job_detail.html'

    def get(self, request, pk, *args, **kwargs): # Changed job_id to pk for consistency with reverse calls
        job = get_object_or_404(Job, pk=pk)
        context = {'job': job}
        if request.user.is_authenticated and hasattr(request.user, 'candidate_profile'): # Check candidate_profile directly on user
            candidate = request.user.candidate_profile
            if candidate and candidate.resumes.exists():
                context['application_exists'] = Application.objects.filter(candidate=candidate, job=job).exists()
            else:
                context['application_exists'] = False
        else:
            context['application_exists'] = False

        return render(request, self.template_name, context)


class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'jobs/job_create.html'
    form_class = JobForm
    success_url = reverse_lazy('jobs:job_list')

    def test_func(self):
        # Ensure user has a profile and is a recruiter
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user # Assign the current user as the poster
            job.save()
            messages.success(request, f"Job '{job.title}' posted successfully.")
            return redirect(self.success_url)
        else:
            context = {'form': form}
            return render(request, self.template_name, context)

class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'jobs/job_edit.html'
    form_class = JobForm
    model = Job

    def test_func(self):
        # Basic check for recruiter role. Ownership check happens in get_object.
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get_object(self, pk): # Changed job_id to pk
        """Helper to get the job object and perform ownership/permission check."""
        job = get_object_or_404(self.model, pk=pk)
        if self.request.user != job.posted_by and not self.request.user.profile.role == 'admin':
            # Use messages for feedback if this is not handled by test_func or redirect
            raise PermissionError("You do not have permission to edit this job.")
        return job

    def get(self, request, pk, *args, **kwargs): # Changed job_id to pk
        try:
            job = self.get_object(pk)
            # Double check permission as test_func is class-level
            if request.user != job.posted_by and not request.user.profile.role == 'admin':
                messages.error(request, "You do not have permission to edit this job.")
                return redirect('jobs:recruiter_applications')

            form = self.form_class(instance=job)
            context = {'form': form, 'job': job}
            return render(request, self.template_name, context)
        except PermissionError:
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

    def post(self, request, pk, *args, **kwargs): # Changed job_id to pk
        try:
            job = self.get_object(pk)
            if request.user != job.posted_by and not request.user.profile.role == 'admin':
                messages.error(request, "You do not have permission to edit this job.")
                return redirect('jobs:recruiter_applications')

            form = self.form_class(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, f"Job '{job.title}' updated successfully.")
                return redirect('jobs:recruiter_applications')
            else:
                context = {'form': form, 'job': job}
                return render(request, self.template_name, context)
        except PermissionError:
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'jobs/job_confirm_delete.html'
    model = Job
    success_url = reverse_lazy('jobs:recruiter_applications')

    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get_object(self, pk): # Changed job_id to pk
        job = get_object_or_404(self.model, pk=pk)
        if self.request.user != job.posted_by and not self.request.user.profile.role == 'admin':
            raise PermissionError("You do not have permission to delete this job.")
        return job

    def get(self, request, pk, *args, **kwargs): # Changed job_id to pk
        try:
            job = self.get_object(pk)
            if request.user != job.posted_by and not request.user.profile.role == 'admin':
                messages.error(request, "You do not have permission to delete this job.")
                return redirect('jobs:recruiter_applications')

            context = {'job': job}
            return render(request, self.template_name, context)
        except PermissionError:
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

    def post(self, request, pk, *args, **kwargs): # Changed job_id to pk
        try:
            job = self.get_object(pk)
            if request.user != job.posted_by and not request.user.profile.role == 'admin':
                messages.error(request, "You do not have permission to delete this job.")
                return redirect('jobs:recruiter_applications')

            job_title = job.title
            job.delete()
            messages.success(request, f"Job '{job_title}' deleted successfully.")
            return redirect(self.success_url)
        except PermissionError:
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('jobs:recruiter_applications')

class RecruiterJobApplicationsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'jobs/recruiter_job_applications.html'

    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get(self, request, *args, **kwargs):
        recruiter_jobs = Job.objects.filter(posted_by=request.user)
        # Optimized to fetch related objects in one go
        applications = Application.objects.filter(job__in=recruiter_jobs).select_related(
            'candidate__user_profile__user', 'job' # Fetch user related to candidate's profile
        ).order_by('-applied_at')

        context = {
            'applications': applications,
            'recruiter_jobs': recruiter_jobs,
        }
        return render(request, self.template_name, context)

class ResumeAIReviewView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View to trigger AI screening for a specific Application.
    This includes resume parsing and then AI scoring.
    """
    def test_func(self):
        # Ensure user has a profile and is a recruiter
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def post(self, request, application_id, *args, **kwargs):
        try:
            app = Application.objects.get(pk=application_id)
            
            # Check if the recruiter owns the job related to this application
            if app.job.posted_by != request.user:
                messages.error(request, "You do not have permission to review this application's resume.")
                return redirect('jobs:recruiter_applications')

            resume = None
            # Retrieve the latest resume for the candidate linked to this application
            if hasattr(app.candidate, 'resumes') and app.candidate.resumes.exists():
                resume = app.candidate.resumes.order_by('-uploaded_at').first()

            if not resume or not resume.resume_file: # Check if resume or resume_file exists
                messages.error(request, "No resume file found for this candidate. Please ensure a resume is uploaded.")
                return redirect('jobs:recruiter_applications')

            # --- Step 1: Resume Parsing ---
            # Set parse_status to 'parsing' before starting the process
            resume.parse_status = 'parsing'
            resume.save(update_fields=['parse_status']) # Save just this field for immediate feedback

            parsed_data = parse_resume_with_api(resume.resume_file) # Pass the file object

            if parsed_data:
                resume.parsed_data = parsed_data # Store parsed data
                # No need to set parse_status to 'success' here; it will be set after AI screening
                # For now, keep it as 'parsing' until AI completes or if AI fails.
            else:
                resume.parse_status = 'failed' # Mark parsing as failed if parse_resume_with_api returns None
                resume.save(update_fields=['parse_status'])
                messages.error(request, f"Failed to parse resume for {app.candidate}.")
                return redirect('jobs:recruiter_applications')

            # --- Step 2: AI Screening ---
            job_description = app.job.description or ""
            
            score, feedback = perform_ai_screening(parsed_data, job_description) # Pass parsed data

            resume.ai_resume_score = score
            resume.ai_feedback = feedback
            resume.parse_status = 'success' # Final status is success after AI screening
            resume.save() # Save all AI results and final parse_status

            app.status = 'screening' # Update application status
            app.save()

            messages.success(request, f"AI screening completed for {app.candidate} on '{app.job.title}'. Score: {score:.2f}")
            return redirect('jobs:recruiter_applications')

        except Application.DoesNotExist:
            messages.error(request, "Application not found.")
            return redirect('jobs:recruiter_applications')
        except PermissionError: # Catches the custom PermissionError from get_object
            messages.error(request, "You do not have permission to access this application.")
            return redirect('jobs:recruiter_applications')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during AI screening: {e}")
            # Log the error for debugging
            print(f"Error in ResumeAIReviewView: {e}")
            return redirect('jobs:recruiter_applications')