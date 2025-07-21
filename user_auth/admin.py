from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobile')  # Display these fields in the admin list view
    search_fields = ('user__username', 'mobile')  # Add search functionality

