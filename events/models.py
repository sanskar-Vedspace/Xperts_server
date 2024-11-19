from django.db import models
from django.conf import settings
from core.models import Mentor
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import re


def validate_youtube_url(value):
    youtube_regex = (
        r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
    )
    if not re.match(youtube_regex, value):
        raise ValidationError(
            'Invalid YouTube URL',
            params={'value': value},
        )

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    mentor = models.ForeignKey(Mentor, related_name='events', on_delete=models.CASCADE)
    takeaways = models.TextField(blank=True, null=True)
    introductory_video = models.URLField(blank=True, null=True, validators=[validate_youtube_url])
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    photo = models.ImageField(upload_to='event_photos/', blank=True, null=True)
    background_image = models.ImageField(upload_to='event_backgrounds/', blank=True, null=True)  # New background image field
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Only create slug if not present
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.title

    @property
    def participants(self):
        return [registration.user for registration in self.registrations.all()]


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='event_registrations', on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    class Meta:
        unique_together = ('event', 'user')

    def __str__(self):
        return f'{self.user.username} registered for {self.event.title}'

class EventPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_registration = models.OneToOneField(EventRegistration, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], default='Pending')
    razorpay_order_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.event_registration.event.title} - {self.amount}'
