# ai_recruitment_platform/users/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import UserProfile # Import UserProfile
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_saved
from allauth.socialaccount.models import SocialAccount
from django.dispatch import receiver

User = get_user_model()

# --- Custom Account Adapter ---
class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to manage account-related logic, especially redirects after social signup.
    """
    def is_open_for_signup(self, request, sociallogin=None):
        # Override to allow signup and potentially check role requirement
        return True

    def get_login_redirect_url(self, request):
        """
        Redirects the user after login.
        If the user is new, or their role needs to be selected, redirect to role selection.
        """
        if request.user.is_authenticated:
            try:
                user_profile = request.user.profile
                # Check if role needs to be set (e.g., if it's default or not explicitly chosen)
                # A more robust way is to have a flag like 'role_assigned' or check if role is unset.
                # For now, let's assume if role is 'candidate' and no explicit choice was made, prompt.
                # A better approach for role selection is to intercept *signup*.
                
                # For the specific flow "asked to select your role":
                # This should ideally happen *after* initial signup, not just login.
                # If the user has a role, redirect them to their appropriate dashboard.
                if user_profile.role != 'candidate': # If they are a recruiter or admin
                    return redirect('home') # Or a recruiter dashboard URL
                else:
                    # If role is 'candidate', check if profile setup is complete (e.g. has a resume)
                    # or if explicit role choice is needed.
                    # For now, if they are candidate, we assume they are okay, or redirect to profile.
                    # The prompt says "select your role: Candidate / Recruiter", implying a choice.
                    # This implies that when a NEW user signs up (especially social), we check this.
                    pass # If role is 'candidate', we'll assume it's fine for now, or redirect to profile.

            except UserProfile.DoesNotExist:
                # This is unlikely if signals are working, but handle it.
                messages.error(request, "UserProfile not found.")
                return '/home/' # Fallback redirect

        # If not authenticated or other issues, redirect to homepage/login
        return '/'


# --- Custom Social Account Adapter ---
# This adapter intercepts the saving of social accounts and user data.
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle post-social-login logic, like role selection.
    """
    def is_open_for_signup(self, request, sociallogin=None):
        """Allow signup via social account."""
        return True

    def populate_user_social_account(self, socialuser, data):
        """
        Populate user and social_account objects from social login data.
        This is where you map data from Google (like name) to your Django User/UserProfile.
        """
        user = socialuser.user
        # Map first and last name from Google data to Django User fields
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        # Ensure the email address is marked as verified if it comes from Google
        # (Allauth handles this implicitly if scope is 'email' and verification is 'none')
        
        socialuser.save()
        user.save()
        return socialuser