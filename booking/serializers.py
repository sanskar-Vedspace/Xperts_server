from rest_framework import serializers
from .models import Booking
from scheduling.models import Availability, TimeSlot

class BookingSerializer(serializers.ModelSerializer):
    availability = serializers.PrimaryKeyRelatedField(queryset=Availability.objects.all())
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())

    class Meta:
        model = Booking
        fields = ['availability', 'time_slot', 'start_time', 'end_time', 'payment_status']

    def create(self, validated_data):
        availability = validated_data['availability']
        time_slot = validated_data['time_slot']
        start_time = validated_data['start_time']
        end_time = validated_data['end_time']
        mentee = self.context['request'].user  # Mentee is the logged-in user
        mentor = availability.mentor  # Mentor is inferred from availability

        # Ensure the time slot and availability are for the same mentor
        if time_slot.mentor != mentor:
            raise serializers.ValidationError("The selected time slot does not belong to the specified mentor.")
        
        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            mentor=mentor,
            availability=availability,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_bookings.exists():
            raise serializers.ValidationError("The selected time slot is already booked.")

        return Booking.objects.create(
            mentor=mentor,
            mentee=mentee,
            availability=availability,
            time_slot=time_slot,
            start_time=start_time,
            end_time=end_time,
            payment_status=False  # Set default to false for new bookings
        )
