from django.contrib import admin
from .models import Availability, TimeSlot

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'date', 'start_time', 'end_time')
    list_filter = ('mentor', 'date')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'duration', 'price')
    list_filter = ('mentor', 'duration')



