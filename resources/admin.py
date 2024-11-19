from django.contrib import admin
from .models import Resource, Video

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    inlines = [VideoInline]
