# ai_recruitment_platform/users/admin.py

from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin): # Renamed from UserProfileAdmin to UserProfileAdminInstance
    list_display = ('user', 'role', 'phone_number', 'created_at', 'updated_at')
    list_filter = ('role', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number', 'role')
    readonly_fields = ('user', 'created_at', 'updated_at')