# navigation/models.py
from django.db import models

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='submenus')
    order = models.IntegerField(default=0)
    is_button = models.BooleanField(default=False)  # For buttons like "Browse mentors"

    def __str__(self):
        return self.title


class NavigationSettings(models.Model):
    normal_logo = models.ImageField(upload_to='logos/', help_text="Upload logo for the normal header.")
    sticky_logo = models.ImageField(upload_to='logos/', help_text="Upload logo for the sticky header.")

    def __str__(self):
        return "Navigation Settings"
