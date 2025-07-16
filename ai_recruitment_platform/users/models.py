# ai_recruitment_platform/users/models.py

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
# --- CORRECT THIS IMPORT AND THE DECORATOR ---
# from allauth.socialaccount.signals import social_account_saved # Incorrect signal name
from allauth.socialaccount.signals import social_account_added # <<< CORRECTED SIGNAL NAME
# --- END CORRECT ---

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model

# --- Models ---
ROLE_CHOICES = [
    ('candidate', 'Candidate'),
    ('recruiter', 'Recruiter'),
    ('admin', 'Admin'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True,
        verbose_name='User Account'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='candidate',
        blank=True,
        null=True,
        help_text='The role of the user in the platform.'
    )
    # --- Flag to track role selection ---
    role_selection_completed = models.BooleanField(default=False)

    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text='Optional phone number.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Use get_username() for robustness across different user models
        return f"{self.user.get_username()} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

# --- Signals ---

# Signal for standard Django User creation
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile_for_django_user(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'role_selection_completed': False})

# Signal for allauth user signup (handles email/password and social signups)
@receiver(user_signed_up)
def handle_allauth_signup(sender, request, user, **kwargs):
    """
    Handles user signup via allauth signals.
    Ensures UserProfile is created with a default role and flags for role selection.
    """
    try:
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role_selection_completed': False}
        )
        
        # Check if signup was via social account
        sociallogin = kwargs.get('sociallogin') # Get the sociallogin object if available
        
        if sociallogin: # If it was a social signup (like Google)
            # We want to manage the role selection.
            # If the user is new, or their role is not explicitly set,
            # we need to ensure they are prompted.
            # The 'role_selection_completed' flag helps with this.
            
            # If the role is still the default 'candidate' and not yet selected/confirmed
            # or if it's the very first time the user is associated with a social account
            # we want to mark that role selection is pending.
            if user_profile.role == 'candidate' and not user_profile.role_selection_completed:
                user_profile.role_selection_completed = False # Ensure the flag is False to trigger role selection
                user_profile.save()

    except Exception as e:
        print(f"Error in user_signed_up signal: {e}")
        # Log this error for debugging

# --- CORRECTED Signal Receiver for social_account_added ---
@receiver(social_account_added) # <<< CORRECTED SIGNAL NAME
def handle_social_account_added(sender, request, sociallogin, **kwargs):
    """
    Handler for when a social account is ADDED to a user.
    This signal fires after a social login/signup is processed by allauth.
    Ensures UserProfile exists and sets up the role selection flag.
    """
    user = sociallogin.user # The Django User object linked to the social account
    
    try:
        # Ensure UserProfile exists with default role and selection flag
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role_selection_completed': False} # Default flag for role selection
        )
        
        # If the UserProfile was just created, or if the role needs explicit selection (e.g., it's still default 'candidate')
        if created or (user_profile.role == 'candidate' and not user_profile.role_selection_completed):
            # Mark that role selection is pending.
            # This flag will be checked by a middleware or a custom redirect logic
            # after the user is logged in to redirect them to the role selection page.
            user_profile.role_selection_completed = False
            user_profile.save()
            
    except UserProfile.DoesNotExist:
        print(f"UserProfile not found for user {user.get_username()} after social account added.")
    except Exception as e:
        print(f"Error in social_account_added signal handler: {e}")