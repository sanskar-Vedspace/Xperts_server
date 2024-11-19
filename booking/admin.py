from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'start_time', 'end_time', 'payment_status', 'created_at')
    list_filter = ('mentor', 'payment_status')
    search_fields = ('mentor__username', 'mentee__username')
