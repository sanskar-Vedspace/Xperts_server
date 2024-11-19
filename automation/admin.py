from django.contrib import admin
from .models import GoogleCredentials

@admin.register(GoogleCredentials)
class GoogleCredentialsAdmin(admin.ModelAdmin):
    list_display = ['user']
