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
import os # Needed for os.environ.get
import json # For json.dumps and json.loads
import logging # For logging errors

# Import models and forms from other apps
from .models import Job
from .forms import JobForm
from applications.models import Application
from candidates.models import Resume # Need Resume model for screening

# --- Helper Functions for Resume Parsing and AI Screening ---

def parse_resume_with_api(resume_file):
    """
    Simulates calling an external resume parsing API (e.g., Hugging Face model).
    Returns a dictionary of parsed data or None on failure.
    """
    if not resume_file:
        return None

    # In a real scenario, you'd call an API here.
    # This simulation uses the structure you provided.
    try:
        # If resume_file is a Django UploadedFile, its path is available.
        # For simulation, we'll just check if it exists.
        # If resume_file is None or doesn't have a path, we simulate failure.
        if not hasattr(resume_file, 'path') or not os.path.exists(resume_file.path):
             print("Simulated parsing: Resume file path invalid or missing.")
             return None

        # Simulate reading file content and extracting basic info
        with open(resume_file.path, 'rb') as f:
            resume_text = f.read().decode('utf-8', errors='ignore')
        
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

def perform_ai_screening(parsed_resume_data, job_description):
    """
    Simulates AI scoring based on parsed resume data and job description.
    In a real scenario:
    1. Use OpenAI GPT-4 or similar.
    2. Prompt the AI with parsed_resume_data and job_description.
    3. Return a score and feedback.
    """
    score = 0.0
    feedback_parts = []

    if parsed_resume_data and job_description:
        # Simulate scoring based on presence of certain keys and job description length
        score_factors = 0
        
        # Accessing data from parsed_resume_data (structure from your example output)
        overall_score_from_parsed = parsed_resume_data.get("overall_score")
        if overall_score_from_parsed is not None:
            score = float(overall_score_from_parsed)
            feedback_parts.append(f"Overall AI Score: {score:.2f}%. ")
        
        sections = parsed_resume_data.get("sections", {})
        for section_name, section_data in sections.items():
            if section_data.get("missing"):
                feedback_parts.append(f"Missing in {section_name}: {section_data['missing']}. ")
            # Use comment if available and not too long
            comment = section_data.get("comment", "")
            if comment and len(comment) < 150: # Keep feedback concise
                feedback_parts.append(f"[{section_name.capitalize()}]: {comment[:100]}... ") # Truncate comment

        # If no specific feedback, provide a general statement
        if not feedback_parts:
            feedback = "AI analysis complete. No specific missing items or suggestions found in simulated data."
        else:
            feedback = "".join(feedback_parts)

        score = min(max(score, 0.0), 100.0) # Cap score at 100

    else:
        score = 0.0
        feedback = "Could not perform screening due to missing parsed data or job description."

    return score, feedback

# --- View Classes ---

class JobListView(View):
    template_name = 'jobs/job_list.html'
    def get(self, request, *args, **kwargs):
        jobs = Job.objects.filter(is_active=True, status='open').order_by('-published_date')
        context = {'jobs': jobs}
        return render(request, self.template_name, context)

class JobDetailView(View):
    template_name = 'jobs/job_detail.html'
    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job, pk=pk)
        context = {'job': job}
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            try:
                candidate = request.user.profile.candidate_profile # Access candidate profile via UserProfile
                if candidate and candidate.resumes.exists():
                    context['application_exists'] = Application.objects.filter(candidate=candidate, job=job).exists()
                else:
                    context['application_exists'] = False
            except AttributeError: # Handle cases where UserProfile or candidate_profile might not exist
                context['application_exists'] = False
        else:
            context['application_exists'] = False
        return render(request, self.template_name, context)

class JobCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'jobs/job_create.html'
    form_class = JobForm
    success_url = reverse_lazy('jobs:job_list')

    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
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
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def get_object(self, pk):
        job = get_object_or_404(self.model, pk=pk)
        if self.request.user != job.posted_by and not self.request.user.profile.role == 'admin':
            raise PermissionError("You do not have permission to edit this job.")
        return job

    def get(self, request, pk, *args, **kwargs):
        try:
            job = self.get_object(pk)
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

    def post(self, request, pk, *args, **kwargs):
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

    def get_object(self, pk):
        job = get_object_or_404(self.model, pk=pk)
        if self.request.user != job.posted_by and not self.request.user.profile.role == 'admin':
            raise PermissionError("You do not have permission to delete this job.")
        return job

    def get(self, request, pk, *args, **kwargs):
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

    def post(self, request, pk, *args, **kwargs):
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
    View to trigger resume parsing and AI screening for a specific Application.
    This includes resume parsing and then AI scoring.
    """
    def test_func(self):
        # Ensure user has a profile and is a recruiter
        return hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'recruiter'

    def post(self, request, application_id, *args, **kwargs):
        try:
            app = Application.objects.get(pk=application_id)
            
            # Check if the recruiter owns the job related to this application
            if request.user.profile.role == 'recruiter' and request.user != app.job.posted_by:
                messages.error(request, "You do not have permission to review this application's resume.")
                return redirect('jobs:recruiter_applications')

            resume = None
            # Retrieve the latest resume for the candidate linked to this application
            # NOTE: The Application model should ideally have a FK to Resume for precise linking.
            # For now, we fetch the latest resume for the candidate as a fallback.
            if hasattr(app.candidate, 'resumes') and app.candidate.resumes.exists():
                resume = app.candidate.resumes.order_by('-uploaded_at').first()

            if not resume or not resume.resume_file: # Check if resume object or file exists
                messages.error(request, "No resume file found for this candidate. Please ensure a resume is uploaded.")
                return redirect('jobs:recruiter_applications')

            # --- Step 1: Resume Parsing ---
            # Set parse_status to 'parsing' before starting the process
            resume.parse_status = 'parsing'
            resume.save(update_fields=['parse_status']) # Save only this field for immediate UI update

            parsed_data = parse_resume_with_api(resume.resume_file) # Call the parsing function

            if parsed_data:
                resume.parsed_data = parsed_data # Store parsed data
                # Parsing was successful, but AI screening is next, so keep status as 'parsing'
            else:
                resume.parse_status = 'failed' # Mark parsing as failed
                resume.save(update_fields=['parse_status']) # Save failure status
                messages.error(request, f"Failed to parse resume for {app.candidate}.")
                return redirect('jobs:recruiter_applications')

            # --- Step 2: AI Screening ---
            # Only proceed to AI screening if parsing was successful
            if resume.parse_status == 'success' and resume.parsed_data: # Check if parsing was successful and data is available
                # Get the text content for AI screening. Use parsed_data if available, otherwise fallback to raw text.
                resume_text_for_ai = ""
                if resume.parsed_data:
                    # Extract relevant text from parsed_data. Structure depends on the parser.
                    # For the simulated data: combine summary, comments, and potentially killer_quote.
                    combined_text_parts = []
                    if summary := parsed_data.get("summary"): combined_text_parts.append(summary)
                    sections = parsed_data.get("sections", {})
                    for section_data in sections.values():
                        if comment := section_data.get("comment"):
                            combined_text_parts.append(comment)
                    if killer_quote := parsed_data.get("killer_quote"):
                        combined_text_parts.append(killer_quote)
                    resume_text_for_ai = " ".join(combined_text_parts)
                elif resume.resume_file: # Fallback to raw file content if parsed_data is not usable as text
                    try:
                        resume.resume_file.seek(0)
                        resume_text_for_ai = resume.resume_file.read().decode('utf-8', errors='ignore')
                    except Exception as file_err:
                        messages.error(request, f"Error reading resume file for AI: {file_err}")
                        resume.parse_status = 'failed' # Mark as failed if file read fails
                        resume.save(update_fields=['parse_status'])
                        return redirect('jobs:recruiter_applications')

                job_description = app.job.description or ""

                # Update status to 'parsing' before calling AI
                resume.parse_status = 'parsing'
                resume.save(update_fields=['parse_status'])

                # Call the AI screening function
                score, feedback = perform_ai_screening(resume.parsed_data or {'text': resume_text_for_ai}, job_description)

                # Update Resume with AI results
                resume.ai_resume_score = score
                resume.ai_feedback = feedback
                resume.parse_status = 'success' # Final status after AI screening
                resume.save()

                # Update Application status to indicate AI review is done
                app.status = 'screening'
                app.save()

                messages.success(request, f"AI screening completed for {app.candidate} on '{app.job.title}'. Score: {score:.2f}")
            else:
                # If parsing failed, the error message was already displayed.
                messages.warning(request, "AI screening could not be performed due to parsing failure.")

            return redirect('jobs:recruiter_applications')

        except Application.DoesNotExist:
            messages.error(request, "Application not found.")
            return redirect('jobs:recruiter_applications')
        except PermissionError:
            messages.error(request, "You do not have permission to access this application.")
            return redirect('home')
        except Exception as e:
            messages.error(request, f"An error occurred during AI screening: {e}")
            # Log the error for debugging
            logging.error(f"AI Screening Error: {e}", exc_info=True)
            return redirect('jobs:recruiter_applications')