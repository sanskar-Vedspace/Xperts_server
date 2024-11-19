from rest_framework import serializers
from .models import TimeBlock

class TimeBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBlock
        fields = ['id', 'duration']

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive number.")
        return value
