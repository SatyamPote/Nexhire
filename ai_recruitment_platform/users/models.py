# ai_recruitment_platform/users/models.py

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_saved
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
# Ensure your Django User model is correctly referenced
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
        default='candidate', # Default role
        blank=True, # Make role blank initially if we want explicit selection
        null=True,
        help_text='The role of the user in the platform.'
    )
    # --- NEW FIELD TO TRACK ROLE SELECTION ---
    role_selection_completed = models.BooleanField(default=False) # Flag to track if role was explicitly chosen

    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text='Optional phone number.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

# --- Signals ---

# Signal for standard Django User creation (e.g., via admin or custom script)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile_for_django_user(sender, instance, created, **kwargs):
    if created:
        # Create UserProfile with a default role and role_selection_completed = False
        UserProfile.objects.get_or_create(user=instance, defaults={'role_selection_completed': False})

# Signal for allauth user signup (handles email/password and social signups)
@receiver(user_signed_up)
def handle_allauth_signup(sender, request, user, **kwargs):
    """
    Handles user signup via allauth signals.
    Ensures UserProfile is created with a default role and flags for role selection.
    """
    try:
        # Ensure UserProfile exists with default role and selection flag
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role_selection_completed': False} # Default role is set in model, this ensures the flag is False
        )
        
        # If the signup was via social account, we need to check if role needs selection.
        # allauth provides sociallogin object via request.POST.get('sociallogin') in some flows,
        # or via kwargs if it's passed through signals.
        # For simplicity here, we rely on the 'role_selection_completed' flag.
        # If the user is new, and role_selection_completed is False, they'll be prompted later.
        
    except Exception as e:
        print(f"Error in user_signed_up signal: {e}")

# Signal to save UserProfile when User is saved (for updates)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the UserProfile instance when the User instance is saved.
    This is primarily for updates, but also ensures linkage.
    """
    # Ensure the profile exists if the user does.
    # Note: Signals can sometimes run multiple times or in unexpected orders.
    # The get_or_create in the signals above is safer.
    if hasattr(instance, 'profile'):
        instance.profile.save()