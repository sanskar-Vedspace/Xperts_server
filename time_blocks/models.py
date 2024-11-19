from django.db import models

class TimeBlock(models.Model):
    duration = models.PositiveIntegerField()  # Duration in minutes

    def __str__(self):
        return f'{self.duration} minutes'
