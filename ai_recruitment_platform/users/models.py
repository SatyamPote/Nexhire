# ai_recruitment_platform/users/models.py

# <<< ADD THIS IMPORT >>>
from django.db import models
# <<< END ADDITION >>>

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define choices for user roles
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
        help_text='The role of the user in the platform.'
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text='Optional phone number.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

# --- Signals ---

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={'role': 'candidate'})

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

# --- Signal for allauth user signup ---
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def handle_allauth_signup(sender, request, user, **kwargs):
    try:
        UserProfile.objects.get_or_create(user=user, defaults={'role': 'candidate'})
    except Exception as e:
        print(f"Error in user_signed_up signal: {e}")