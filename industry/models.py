from django.db import models

class Expertise(models.Model):
    name = models.CharField(max_length=255)
    expertise_description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name
