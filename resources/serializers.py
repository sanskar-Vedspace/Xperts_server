from rest_framework import serializers
from .models import Resource, Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'video_url','category','description']

class ResourceSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True)

    class Meta:
        model = Resource
        fields = ['title', 'description', 'videos']
