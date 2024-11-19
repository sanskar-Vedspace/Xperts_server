from django.db import models
from core.models import Mentor, CustomUser
from django.core.exceptions import ValidationError 
import re# Assuming this is defined in core/validators.py
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

def validate_youtube_url(value):
    youtube_regex = (
        r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
    )
    if not re.match(youtube_regex, value):
        raise ValidationError(
            'Invalid YouTube URL',
            params={'value': value},
        )

class Cohort(models.Model):
    mentor = models.ForeignKey(Mentor, related_name='cohorts', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    takeaways = models.TextField()
    introductory_video = models.URLField(validators=[validate_youtube_url], blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    link = models.URLField()
    start_date = models.DateTimeField(default=timezone.now() + timedelta(days=30))  # Default value set to 30 days from now
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=30))  # Default value set to 30 days from now

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Cohort.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def participants(self):
        return [registration.user.username for registration in self.registrations.all()]


class CohortRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cohort_registrations')
    cohort = models.ForeignKey(Cohort, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending')

    def __str__(self):
        return f'{self.user.username} - {self.cohort.name}'

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    from django.db import models
from core.models import CustomUser

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cohort_registration = models.OneToOneField(CohortRegistration, on_delete=models.CASCADE, related_name='payment', null=True, blank= True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Success', 'Success'), ('Failed', 'Failed')], default='Pending')
    razorpay_order_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)  # Signature from Razorpay
    verified = models.BooleanField(default=False)  # Verification status

    def __str__(self):
        return f'{self.user.username} - {self.cohort_registration.cohort.name} - {self.amount}'