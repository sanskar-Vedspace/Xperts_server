from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.core.exceptions import ValidationError
import re
from tools.models import Tool
from industry.models import Expertise
from articles.models import Article
from workex.models import WorkExperience
from django.conf import settings
from time_blocks.models import TimeBlock
from datetime import date, timedelta, datetime

class Review(models.Model):
    mentor = models.ForeignKey('Mentor', related_name='mentor_reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'Review for {self.mentor.name} by {self.reviewer.username if self.reviewer else "Admin"}'

def validate_youtube_url(value):
    youtube_regex = (
        r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
    )
    if not re.match(youtube_regex, value):
        raise ValidationError(
            'Invalid YouTube URL',
            params={'value': value},
        )

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, user_type='mentee', **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('mentor', 'Mentor'),
        ('mentee', 'Mentee'),
    )

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    interests = models.ManyToManyField(Expertise, related_name='mentees', blank=True)
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pin = models.CharField(max_length=10, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    short_intro = models.TextField(blank=True, null=True)
    age_of_startup = models.IntegerField(blank=True, null=True)
    industry_of_startup = models.CharField(max_length=100, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='mentee')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_set', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def convert_to_mentor(self):
        if self.user_type == 'mentee':
            self.user_type = 'mentor'
            self.save()
            Mentor.objects.create(username=self, name=self.username)

class Mentor(models.Model):
    username = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='mentor_profile')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    short_intro = models.TextField(blank=True, null=True)
    introductory_video = models.URLField(blank=True, null=True, validators=[validate_youtube_url])
    expertise = models.ManyToManyField(Expertise, related_name='mentors', blank=True)
    toolkits_used = models.ManyToManyField(Tool, related_name='mentors', blank=True)
    experience = models.ManyToManyField(WorkExperience, related_name='mentors', blank=True)
    content_links = models.ManyToManyField(Article, related_name='articles', blank=True)
    reviews = models.ManyToManyField(Review, related_name='mentor_reviews', blank=True)
    linkedin = models.URLField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    location=models.CharField(max_length=255,default='Noida')
    joined_date = models.DateField(default=date.today)  # Automatically set to the date the mentor is created
    availabilities = models.ManyToManyField('Availability', related_name='mentors', blank=True)
    time_slots = models.ManyToManyField('TimeSlot', related_name='mentors', blank=True)
    @property
    def next_availability(self):
        # Get the next availability from the related schedule
        upcoming_availability = self.schedule.filter(date__gte=date.today()).order_by('date', 'start_time').first()
        if upcoming_availability:
            return f'{upcoming_availability.date} at {upcoming_availability.start_time}'
        return "No upcoming availability"

    def __str__(self):
        return self.name
class Availability(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentor_availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def get_available_slots(self, duration):
        slots = []
        start_time = datetime.combine(self.date, self.start_time)
        end_time = datetime.combine(self.date, self.end_time)

        while start_time + timedelta(minutes=duration) <= end_time:
            slot_end_time = start_time + timedelta(minutes=duration)
            
            # Check for overlapping bookings for this mentor and availability
            overlapping_bookings = Booking.objects.filter(
                mentor=self.mentor,
                availability=self,
                start_time__lt=slot_end_time,
                end_time__gt=start_time,
                booking_status__in=['pending', 'approved']  # Consider only pending/approved bookings
            )

            # Add slot only if there are no overlapping bookings
            if not overlapping_bookings.exists():
                slots.append({
                    'start': start_time.time(),
                    'end': slot_end_time.time(),
                })

            start_time = slot_end_time  # Increment to next slot start

        return slots
    def __str__(self):
        return f"{self.mentor.name} on {self.date} from {self.start_time} to {self.end_time}"


class TimeSlot(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentor_time_slots')
    duration = models.PositiveIntegerField()  # in minutes
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('mentor', 'duration')

    def __str__(self):
        return f"{self.mentor.name} - {self.duration} mins at {self.price} INR"

class MentorTimeBlock(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='mentor_time_blocks')
    time_block = models.ForeignKey(TimeBlock, on_delete=models.CASCADE, related_name='mentor_time_blocks')
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('mentor', 'time_block')

    def __str__(self):
        return f'{self.mentor.name} - {self.time_block.duration} minutes - {self.price} INR'

class OTP(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'OTP for {self.user.username}'
    
from django.db import models

class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    payment_status = models.BooleanField(default=False)
    booking_status = models.CharField(
        max_length=10,
        choices=BOOKING_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    meeting_link = models.URLField(max_length=255, null=True, blank=True)
    wallet_payment_status = models.BooleanField(default=True)
    def __str__(self):
        return f'Booking {self.id} for {self.mentee.username} with {self.mentor.name}'



class Payment(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='payment')
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Payment for Booking {self.booking.id} - {self.status}'
