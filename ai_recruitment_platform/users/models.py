# ai_recruitment_platform/users/models.py

from django.db import models
from django.conf import settings # Recommended way to refer to the User model
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define choices for user roles
ROLE_CHOICES = [
    ('candidate', 'Candidate'),
    ('recruiter', 'Recruiter'),
    ('admin', 'Admin'),
]

class UserProfile(models.Model):
    """
    Extends Django's User model to add profile-specific information like roles.
    Links one-to-one with the built-in Django User model.
    """
    # Use settings.AUTH_USER_MODEL for flexibility if you ever swap out the User model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile', # Allows accessing profile from User: user.profile
        verbose_name='User Account'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='candidate', # Default role for new users
        help_text='The role of the user in the platform (e.g., Candidate, Recruiter).'
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text='Optional phone number for the user.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Display the username along with the role
        return f"{self.user.username} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

# --- Signals to automatically create UserProfile when a User is created ---
# This is a common and useful pattern.

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile instance for each new User.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the UserProfile instance when the User instance is saved.
    """
    instance.profile.save()

# --- Admin configuration for UserProfile ---
# Create this file if it doesn't exist in the 'users' app directory.
# File Path: ai_recruitment_platform/users/admin.py

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'created_at', 'updated_at')
    list_filter = ('role', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'role')
    # Make the 'user' field read-only because it's linked via signal and should not be changed manually here.
    readonly_fields = ('user', 'created_at', 'updated_at')
    # Ensure the user field isn't displayed in the 'add' form either if you want strict control.
    # If you want to allow selecting a user, remove readonly_fields for 'user'.
    # For this MVP, it's better to have it auto-created.