from django.contrib import admin
from .models import Event, EventRegistration, EventPayment

class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0  # Set this to 0 to make it optional

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'start_time', 'end_time', 'mentor', 'price')
    search_fields = ('title', 'mentor__username', 'mentor__name')
    list_filter = ('date', 'mentor', 'price')
    ordering = ('date', 'start_time')
    inlines = [EventRegistrationInline]  # The inline is optional now

class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'registration_date', 'payment_status')
    search_fields = ('event__title', 'user__username', 'user__email')
    list_filter = ('registration_date', 'event', 'payment_status')
    ordering = ('registration_date',)

class EventPaymentAdmin(admin.ModelAdmin):
    list_display = ('get_event_title','user',  'amount', 'payment_status', 'payment_date', 'razorpay_order_id', 'razorpay_payment_id', 'verified')
    search_fields = ('user__username', 'event_registration__event__title', 'razorpay_order_id', 'razorpay_signature')
    list_filter = ('payment_status', 'payment_date', 'verified')
    ordering = ('-payment_date',)
    autocomplete_fields = ['event_registration', 'user']

    def get_event_title(self, obj):
        return obj.event_registration.event.title
    get_event_title.short_description = 'Event'

admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration, EventRegistrationAdmin)
admin.site.register(EventPayment, EventPaymentAdmin)
