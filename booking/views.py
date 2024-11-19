from rest_framework import generics, status
from rest_framework.response import Response
from .models import Booking
from .serializers import BookingSerializer
from scheduling.models import Availability, TimeSlot
from core.models import Mentor,Payment
from .razorpay_service import create_razorpay_order, verify_payment
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class CreateBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info("CreateBookingView - Request Data: %s", request.data)

        # Extract required fields from request data
        mentor_id = request.data.get('mentor_id')
        availability_id = request.data.get('availability_id')
        time_slot_id = request.data.get('time_slot_id')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')

        # Validate that required fields are provided
        if not all([mentor_id, availability_id, time_slot_id, start_time, end_time]):
            return Response({"error": "Mentor ID, Availability ID, Time Slot ID, Start Time, and End Time are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the mentor, availability, and time slot instances
        mentor = get_object_or_404(Mentor, id=mentor_id)
        availability = get_object_or_404(Availability, id=availability_id)
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        # Check if the time slot belongs to the selected mentor
        if time_slot.mentor != mentor or availability.mentor != mentor:
            return Response({"error": "Time Slot and Availability do not belong to the selected mentor."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            mentor=mentor,
            availability=availability,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

        if overlapping_bookings.exists():
            return Response({"error": "The selected time slot is already booked."}, status=status.HTTP_409_CONFLICT)

        # Prepare data for the booking
        booking_data = {
            'mentor': mentor.id,
            'mentee': request.user.id,
            'availability': availability.id,
            'time_slot': time_slot.id,
            'start_time': start_time,
            'end_time': end_time,
            'payment_status': False
        }

        # Validate and save the booking using the serializer
        serializer = self.get_serializer(data=booking_data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Create Razorpay order
        amount = time_slot.price * 100  # Razorpay accepts amount in paise
        razorpay_order = client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        # Create a Payment entry linked to the booking
        Payment.objects.create(
            booking=booking,
            razorpay_order_id=razorpay_order['id'],
            amount=time_slot.price,
            status='Pending'
        )

        # Return Razorpay order details for frontend payment processing
        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'amount': amount,
            'currency': 'INR',
            'booking_id': booking.id
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')
        booking_id = request.data.get('booking_id')

        if verify_payment(payment_id, order_id, signature):
            booking = Booking.objects.get(id=booking_id)
            booking.payment_status = True
            booking.save()
            return Response({'status': 'Payment successful, booking confirmed!'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Payment verification failed!'}, status=status.HTTP_400_BAD_REQUEST)
