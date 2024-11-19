from django.contrib import admin
from .models import TimeBlock

class TimeBlockAdmin(admin.ModelAdmin):
    list_display = ('duration',)
    search_fields = ('duration',)
    ordering = ('duration',)

admin.site.register(TimeBlock, TimeBlockAdmin)
