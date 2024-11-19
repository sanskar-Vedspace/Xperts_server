from django.db import models
from django.conf import settings
from industry.models import Expertise  # Import Expertise from industry app
from django.core.validators import FileExtensionValidator
from datetime import timedelta
from django.utils import timezone

# Subscription cycle choices
SUBSCRIPTION_CYCLES = (
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
    ('annual', 'Annual'),
)

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=255)  # Name of the subscription plan
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Monthly price
    quarterly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Quarterly price
    annual_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Annual price

    def __str__(self):
        return self.name

    def get_price_by_cycle(self, cycle):
        """ Return the price based on the selected cycle. """
        if cycle == 'monthly':
            return self.monthly_price
        elif cycle == 'quarterly':
            return self.quarterly_price
        elif cycle == 'annual':
            return self.annual_price
        return None

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    cycle = models.CharField(max_length=10, choices=SUBSCRIPTION_CYCLES, default='monthly')  # Subscription cycle
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.plan.name} - {self.cycle}'

    def calculate_subscription_end_date(self):
        """ Calculate the end date of the subscription based on the cycle. """
        if self.cycle == 'monthly':
            return self.started_at + timedelta(days=30)
        elif self.cycle == 'quarterly':
            return self.started_at + timedelta(days=90)
        elif self.cycle == 'annual':
            return self.started_at + timedelta(days=365)
        return None

    def activate_subscription(self):
        """ Activate the subscription and set the expiration date. """
        self.is_active = True
        self.started_at = timezone.now()
        self.ends_at = self.calculate_subscription_end_date()
        self.save()

    def check_subscription_status(self):
        """ Check if the subscription has expired and deactivate if necessary. """
        if self.ends_at and timezone.now() > self.ends_at:
            self.is_active = False
            self.save()
        return self.is_active

class SubscriptionPayment(models.Model):
    subscription = models.OneToOneField(Subscription, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, unique=True)  # Razorpay payment ID
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)  # Razorpay order ID

    def __str__(self):
        return f'Payment for {self.subscription.user.username} - {self.subscription.plan.name}'

class Group(models.Model):
    name = models.CharField(max_length=255)
    expertise = models.ForeignKey(Expertise, on_delete=models.CASCADE, related_name='groups')  # Link to Expertise
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='community_groups')

    def __str__(self):
        return self.name

class Post(models.Model):
    POST_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('poll', 'Poll'),
        ('document', 'Document'),
        ('pdf', 'PDF'),
        ('link', 'Link'),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # Default to text
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='community/images/', null=True, blank=True)
    document = models.FileField(
        upload_to='community/documents/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['doc', 'docx', 'txt'])]
    )
    pdf = models.FileField(
        upload_to='community/pdfs/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    poll_options = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group, related_name='posts', on_delete=models.CASCADE)
    expertise = models.ForeignKey(Expertise, on_delete=models.CASCADE, related_name='posts')

    def __str__(self):
        return f'{self.author} - {self.content_type}'

class Like(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Like by {self.user.username} on {self.post.id}'

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.id}'

class Share(models.Model):
    post = models.ForeignKey(Post, related_name='shares', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Share by {self.user.username} on {self.post.id}'

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f'{self.follower.username} follows {self.followed.username}'
