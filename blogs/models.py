from django.db import models
from django.conf import settings
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField
from taggit.managers import TaggableManager
from core.models import CustomUser  # Import CustomUser model

# New Category Model
class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Reference to CustomUser
    content = RichTextUploadingField()
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO and OG fields
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    og_title = models.CharField(max_length=255, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = models.ImageField(upload_to='og_images/', blank=True, null=True)

    # Category field
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name="posts")

    # Keyword tags
    tags = TaggableManager()

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(BlogPost, self).save(*args, **kwargs)