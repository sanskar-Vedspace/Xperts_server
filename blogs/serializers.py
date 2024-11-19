from rest_framework import serializers
from .models import BlogPost, BlogCategory

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['name', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.first_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = BlogPost
        fields = [
            'id', 'category','category_name', 'title', 'content', 'thumbnail', 'created_at', 'updated_at','slug',
            'meta_title', 'meta_description', 'og_title', 'og_description', 'og_image', 'author', 'author_name'
        ]