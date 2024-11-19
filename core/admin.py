from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Mentor, Review, MentorTimeBlock, Availability, TimeSlot, Booking, Payment
from tools.models import Tool
from industry.models import Expertise


# CustomUserAdmin to display profile picture from Mentor model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'profile_picture_thumbnail')
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'user_type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'company_name', 'designation', 'gst_number', 'address', 'country', 'pin', 'state', 'city', 'short_intro', 'age_of_startup','interests', 'industry_of_startup',  'profile_picture')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username', 'email',)

    # Display profile picture thumbnail from Mentor model
    def profile_picture_thumbnail(self, obj):
        if obj.user_type == 'mentor' and hasattr(obj, 'mentor_profile') and obj.mentor_profile.profile_picture:
            return format_html('<img src="{}" style="width: 50px; height:50px;" />', obj.mentor_profile.profile_picture.url)
        return "No picture"
    
    profile_picture_thumbnail.short_description = 'Profile Picture'

# Inline for reviews in the Mentor model
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

# Inline for time blocks in the Mentor model
class MentorTimeBlockInline(admin.TabularInline):
    model = MentorTimeBlock
    extra = 1

# Register Availability and TimeSlot models
@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'date', 'start_time', 'end_time')
    list_filter = ('mentor', 'date')

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'duration', 'price')
    list_filter = ('mentor', 'duration')

# Register Booking and Payment models
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'availability', 'time_slot', 'start_time', 'end_time', 'payment_status','wallet_payment_status')
    list_filter = ('mentor', 'mentee', 'payment_status')
    search_fields = ('mentor__username', 'mentee__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'razorpay_order_id', 'razorpay_payment_id', 'status')
    list_filter = ('status',)
    search_fields = ('razorpay_order_id', 'razorpay_payment_id')

# MentorAdmin for displaying mentor details including reviews and time blocks
class MentorAdmin(admin.ModelAdmin):
    list_display = ('name', 'username')
    filter_horizontal = ('expertise', 'toolkits_used')
    inlines = [ReviewInline, MentorTimeBlockInline]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Mentor, MentorAdmin)
admin.site.register(Tool)
admin.site.register(Expertise)
admin.site.register(Review)
