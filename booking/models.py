from django.db import models
from scheduling.models import Availability, TimeSlot
from django.conf import settings
from core.models import CustomUser

class Booking(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    mentee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentee_bookings')
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='bookings')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.TimeField()
    end_time = models.TimeField()
    payment_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('mentor', 'mentee', 'start_time', 'end_time')

    def __str__(self):
        return f'Booking with {self.mentor.username} by {self.mentee.username} from {self.start_time} to {self.end_time}'
