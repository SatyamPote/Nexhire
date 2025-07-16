# ai_recruitment_platform/users/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from users.models import UserProfile
from django.contrib import messages
from allauth.account.utils import get_adapter as get_allauth_adapter # To access allauth's adapter logic if needed

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to handle post-social-login redirects, particularly for role selection.
    """
    def get_login_redirect_url(self, request):
        """
        Redirects the user after login.
        If the user is authenticated, check their profile role.
        If role is not completed, redirect to role selection.
        """
        if request.user.is_authenticated:
            try:
                user_profile = request.user.profile
                # If role selection is not completed, redirect them to the role selection page
                if not user_profile.role_selection_completed:
                    # Reverse the URL for role selection
                    return reverse('users:role_selection')
                # If role is already completed, use default redirect
                elif user_profile.role == 'recruiter':
                    return reverse('jobs:recruiter_applications') # Recruiter dashboard
                else: # Candidate or other roles
                    return reverse('candidates:candidate_profile') # Candidate dashboard
            except UserProfile.DoesNotExist:
                # If UserProfile is missing, prompt them to complete it or redirect to a setup page
                messages.error(request, "Your profile details are incomplete. Please complete your profile.")
                return reverse('users:role_selection') # Or a specific profile completion page
        
        # If user is not authenticated (e.g., during logout), use default redirect
        return super().get_login_redirect_url(request) # Fallback to default allauth redirect

    # You can also override populate_user on the social adapter if you need to map
    # specific social profile fields to your User model or UserProfile.

# Ensure ACCOUNT_ADAPTER is set in settings.py to point to this adapter