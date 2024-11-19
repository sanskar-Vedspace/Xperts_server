from rest_framework import serializers
from .models import Availability, TimeSlot

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['mentor', 'date', 'start_time', 'end_time']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['mentor', 'duration', 'price']
