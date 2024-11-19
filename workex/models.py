from django.db import models
from django.conf import settings
from industry.models import Expertise

class WorkExperience(models.Model):
    mentor = models.ForeignKey('core.Mentor', related_name='work_experiences', on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=255)
    work_description = models.TextField()
    date_started = models.DateField()
    date_ended = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    industry_expertise = models.ManyToManyField(Expertise, related_name='work_experiences')

    def save(self, *args, **kwargs):
        if self.date_ended is None:
            self.currently_working = True
        else:
            self.currently_working = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.company_name
