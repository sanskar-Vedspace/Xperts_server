from django.db import models

class Resource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='videos')  # Add ForeignKey to Resource
