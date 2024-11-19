from django.db import models
from django.conf import settings
from decimal import Decimal
from core.models import Booking, Mentor


class CommissionSetting(models.Model):
    COMMISSION_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]
    
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPE_CHOICES, default='percentage')
    commission_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on each save
    minimum_payout = models.DecimalField(max_digits=10, decimal_places=2, default=500)

    def __str__(self):
        return f"{self.commission_type} - {self.commission_value} (Min Payout: {self.minimum_payout})"

    def calculate_commission(self, amount):
        """
        Calculate the commission based on the type and value set.
        If the type is 'percentage', it returns the calculated percentage of the amount.
        If the type is 'fixed', it returns the fixed amount as the commission.
        """
        if self.commission_type == 'percentage':
            return (self.commission_value / 100) * amount
        elif self.commission_type == 'fixed':
            return self.commission_value
        return 0  # Default to zero if the commission type is not properly defined



class PaybookEntry(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='paybook_entry')
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='paybook_entries')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    commission_deducted = models.DecimalField(max_digits=10, decimal_places=2)
    credited_to_wallet = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paybook Entry for Booking {self.booking.id} - Credited {self.credited_to_wallet} to {self.mentor.name}'s Wallet"

# paybook/models.py
class PayoutRequest(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='payout_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout Request: {self.mentor.name} - {self.amount} ({self.status})"
