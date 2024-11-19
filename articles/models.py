from django.db import models
from django.conf import settings

class Article(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='articles', on_delete=models.CASCADE)
    def __str__(self):
        return self.title
