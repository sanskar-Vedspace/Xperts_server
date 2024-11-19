from rest_framework import generics, status
from rest_framework.response import Response
from .models import Availability, TimeSlot
from .serializers import AvailabilitySerializer, TimeSlotSerializer
from core.models import CustomUser  # Import Mentor from the correct app
from .razorpay_service import create_razorpay_order, verify_payment
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import date


class AvailabilityListView(generics.ListAPIView):
    queryset = Availability.objects.all()
    serializer_class = AvailabilitySerializer


class TimeSlotListView(generics.ListAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class MentorAvailableSlotsView(generics.ListAPIView):
    """
    Get the available dates and time slots for a mentor
    """
    serializer_class = AvailabilitySerializer

    def get(self, request, mentor_id):
        mentor = get_object_or_404(CustomUser, id=mentor_id)
        availabilities = mentor.availabilities.filter(date__gte=date.today()).order_by('date', 'start_time')
        available_slots = []

        for availability in availabilities:
            for time_slot in mentor.time_slots.all():
                slots = availability.get_available_slots(time_slot.duration)
                available_slots.append({
                    'date': availability.date,
                    'time_slot': time_slot.duration,
                    'price': time_slot.price,
                    'slots': slots
                })

        return Response(available_slots)
