from django.db import models
from datetime import timedelta, date, datetime
from django.conf import settings
from core.models import CustomUser

class Availability(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.mentor.username} - {self.date} ({self.start_time} to {self.end_time})'

    def get_available_slots(self, duration):
        """
        Calculate available time slots in the availability based on the duration
        """
        slots = []
        start_time = datetime.combine(self.date, self.start_time)
        end_time = datetime.combine(self.date, self.end_time)

        while start_time + timedelta(minutes=duration) <= end_time:
            slots.append({
                'start': start_time.time(),
                'end': (start_time + timedelta(minutes=duration)).time(),
            })
            start_time += timedelta(minutes=duration)
        return slots


class TimeSlot(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='time_slots')
    duration = models.PositiveIntegerField()  # duration in minutes (15, 30, 45, 60)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price for the session duration

    class Meta:
        unique_together = ('mentor', 'duration')

    def __str__(self):
        return f'{self.duration} mins - {self.price} INR for {self.mentor.username}'


