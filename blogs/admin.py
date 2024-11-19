from django.contrib import admin
from .models import BlogPost, BlogCategory

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'updated_at')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at', 'updated_at', 'category')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'category', 'content', 'thumbnail', 'tags','slug')
        }),
        ('SEO Fields', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Open Graph Fields', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
    )
