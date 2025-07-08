# ai_recruitment_platform/candidates/admin.py

from django.contrib import admin
from .models import Candidate, Resume
from .forms import CandidateForm

class ResumeInline(admin.TabularInline):
    model = Resume
    extra = 1
    readonly_fields = ('uploaded_at', 'parse_status', 'parsed_data', 'ai_resume_score', 'ai_feedback')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    form = CandidateForm
    list_display = ('full_name', 'email', 'phone', 'linkedin_profile', 'github_profile', 'num_resumes', 'created_at')
    list_filter = ('created_at', 'user_profile__role')
    search_fields = (
        'user_profile__user__first_name',
        'user_profile__user__last_name',
        'user_profile__user__username',
        'user_profile__user__email',
        'linkedin_profile_url',
        'github_profile_url'
    )
    inlines = [ResumeInline]
    readonly_fields = ('user_profile', 'created_at', 'updated_at')

    def full_name(self, obj):
        return obj.user_profile.user.get_full_name() or obj.user_profile.user.username
    full_name.short_description = 'Full Name'

    def email(self, obj):
        return obj.user_profile.user.email
    email.short_description = 'Email'

    def phone(self, obj):
        return obj.phone_number or obj.user_profile.phone_number
    phone.short_description = 'Phone'

    def linkedin_profile(self, obj):
        return obj.linkedin_profile_url
    linkedin_profile.short_description = 'LinkedIn'

    def github_profile(self, obj):
        return obj.github_profile_url
    github_profile.short_description = 'GitHub'

    def num_resumes(self, obj):
        return obj.resumes.count()
    num_resumes.short_description = 'Resumes'