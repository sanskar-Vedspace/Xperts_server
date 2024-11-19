from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from rest_framework.decorators import api_view, permission_classes
import hmac
import hashlib
from django.db import transaction

import threading
from .razorpay_service import verify_payment
from .serializers import UserSerializer,AvailableInterestsSerializer,SuggestedMentorSerializer, LoginSerializer, MentorSerializer, MentorTimeBlockSerializer,BookingSerializer,MenteeBookingSerializer,MenteeProfileSerializer,MentorBookingSerializer
from .models import Mentor, TimeBlock, CustomUser,Expertise, OTP, MentorTimeBlock,Availability,TimeSlot,Booking,Payment
from time_blocks.models import TimeBlock 
from time_blocks.serializers import TimeBlockSerializer
import logging
from django.conf import settings
import razorpay
from django.shortcuts import get_object_or_404 
from datetime import date, timedelta, datetime
import time
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from scheduling.utils import create_google_meet_event
from google.oauth2 import id_token
from google.auth.transport import requests
from paybook.models import PaybookEntry,CommissionSetting
from wallet.models import Wallet,WalletTransaction

User = get_user_model()
logger = logging.getLogger(__name__)

client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def create_razorpay_order(amount):
    # Create an order in Razorpay
    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })
    return order

class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email', None)
        if email and CustomUser.objects.filter(email=email).exists():
            return Response({'exists': True}, status=200)
        return Response({'exists': False}, status=200)
    
class CheckUsernameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username', None)
        if username and CustomUser.objects.filter(username=username).exists():
            return Response({'exists': True}, status=200)
        return Response({'exists': False}, status=200)

class UserProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate OTP
        otp_code = get_random_string(length=6, allowed_chars='0123456789')
        OTP.objects.create(user=user, otp_code=otp_code)

        # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp_code}',
            'menttalk.tech@gmail.com',
            [user.email],
            fail_silently=False,
        )

        return Response({'detail': 'OTP sent to your email. Please verify your account.'}, status=status.HTTP_201_CREATED)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        otp_code = request.data.get('otp_code')
        
        try:
            user = CustomUser.objects.get(username=username)
            otp = OTP.objects.get(user=user, otp_code=otp_code)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Invalid username'}, status=status.HTTP_400_BAD_REQUEST)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if otp.is_verified:
            return Response({'error': 'OTP already verified'}, status=status.HTTP_400_BAD_REQUEST)

        otp.is_verified = True
        otp.save()
        user.is_active = True
        user.save()

        return Response({'detail': 'Account verified successfully'}, status=status.HTTP_200_OK)

class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id, 'user_type': user.user_type})
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class MentorList(generics.ListCreateAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [AllowAny]

class MentorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer
    permission_classes = [AllowAny]

class MentorProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Mentor.objects.all()
    serializer_class = MentorSerializer

    def get_object(self):
        return self.request.user.mentor_profile

    def update(self, request, *args, **kwargs):
        mentor = self.get_object()
        data = request.data

        # Update availability and time slots
        availabilities = data.get('availabilities')
        time_slots = data.get('time_slots')

        if availabilities:
            mentor.availabilities.clear()
            for availability_data in availabilities:
                Availability.objects.create(
                    mentor=mentor,
                    date=availability_data['date'],
                    start_time=availability_data['start_time'],
                    end_time=availability_data['end_time']
                )

        if time_slots:
            mentor.time_slots.clear()
            for time_slot_data in time_slots:
                TimeSlot.objects.create(
                    mentor=mentor,
                    duration=time_slot_data['duration'],
                    price=time_slot_data['price']
                )

        return super().update(request, *args, **kwargs)

class MentorAvailableSlotsView(APIView):
    """
    API view to calculate and return available slots based on mentor availability and time slots.
    """
    permission_classes = [AllowAny]

    def get(self, request, mentor_id):
        # Fetch the mentor and ensure it exists
        mentor = get_object_or_404(Mentor, username_id=mentor_id)
        
        # Get upcoming availabilities for the mentor (only future dates)
        availabilities = mentor.mentor_availabilities.filter(date__gte=date.today()).order_by('date', 'start_time')

        # Get all time slots associated with the mentor
        time_slots = mentor.mentor_time_slots.all()

        available_slots = []

        for availability in availabilities:
            availability_slots = []
            for time_slot in time_slots:
                # Generate available slots for each time slot's duration
                slots = availability.get_available_slots(time_slot.duration)
                if slots:
                    availability_slots.append({
                        'time_slot_id': time_slot.id,
                        'time_slot_duration': time_slot.duration,
                        'price': time_slot.price,
                        'slots': slots
                    })

            if availability_slots:
                available_slots.append({
                    'availability_id': availability.id,
                    'date': availability.date,
                    'start_time': availability.start_time,
                    'end_time': availability.end_time,
                    'slots': availability_slots
                })

        if not available_slots:
            return Response({'message': 'No available slots found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(available_slots, status=status.HTTP_200_OK)


    def generate_slots(self, availability, duration):
        """
        Generates available slots for a given availability and slot duration.
        """
        slots = []
        start_time = datetime.combine(availability.date, availability.start_time)
        end_time = datetime.combine(availability.date, availability.end_time)

        logger.info(f"Generating slots from {start_time} to {end_time} with duration {duration} minutes")

        # Ensure the end time is after the start time
        if end_time <= start_time:
            logger.error("End time is before start time. No slots can be generated.")
            return []

        while start_time + timedelta(minutes=duration) <= end_time:
            end_slot_time = start_time + timedelta(minutes=duration)
            slots.append({
                'start': start_time.time(),
                'end': end_slot_time.time()
            })
            start_time = end_slot_time

        logger.info(f"Generated {len(slots)} slots")
        return slots

def delete_unpaid_booking(booking_id):
    """
    Background thread to delete the booking if payment is not completed after 60 seconds.
    """
    def check_and_delete_unpaid_booking():
        time.sleep(60)  # Wait for 60 seconds
        try:
            booking = Booking.objects.get(id=booking_id)
            if not booking.payment_status:
                logger.info(f"Deleting unpaid booking {booking_id} after 60 seconds.")
                booking.delete()
            else:
                logger.info(f"Booking {booking_id} was paid, not deleting.")
        except Booking.DoesNotExist:
            logger.warning(f"Booking {booking_id} already deleted or does not exist.")

    # Start the background thread
    threading.Thread(target=check_and_delete_unpaid_booking).start()

class CreateBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Extract required fields
        mentor_id = request.data.get('mentor_id')
        availability_id = request.data.get('availability_id')
        time_slot_id = request.data.get('time_slot_id')

        start_time = timezone.make_aware(
            datetime.strptime(request.data.get('start_time'), '%Y-%m-%d %H:%M:%S'),
            timezone.get_current_timezone()
        )
        end_time = timezone.make_aware(
            datetime.strptime(request.data.get('end_time'), '%Y-%m-%d %H:%M:%S'),
            timezone.get_current_timezone()
        )

        # Fetch the mentor, availability, and time slot instances
        mentor = get_object_or_404(Mentor, username_id=mentor_id)
        availability = get_object_or_404(Availability, id=availability_id)
        time_slot = get_object_or_404(TimeSlot, id=time_slot_id)

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            mentor=mentor,
            availability=availability,
            start_time__lt=end_time,
            end_time__gt=start_time,
            booking_status__in=['pending', 'approved']
        )

        if overlapping_bookings.exists():
            return Response({"error": "The selected time slot is already booked."}, status=status.HTTP_409_CONFLICT)

        # Proceed with booking creation if no conflicts
        booking_data = {
            'mentor': mentor,
            'mentee': request.user,
            'availability': availability,
            'time_slot': time_slot,
            'start_time': start_time,
            'end_time': end_time,
            'payment_status': False,
        }

        serializer = self.get_serializer(data=booking_data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        # Start the auto-delete thread for unpaid bookings
        delete_unpaid_booking(booking.id)

        # Create Razorpay order
        try:
            amount = int(time_slot.price * 100)  # Convert price to paise
            razorpay_order = client.order.create({
                'amount': amount,  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'
            })
        except Exception as e:
            logger.error("Error creating Razorpay order: %s", str(e))
            return Response({"error": "Failed to create Razorpay order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create a Payment entry linked to the booking
        Payment.objects.create(
            booking=booking,
            razorpay_order_id=razorpay_order['id'],
            amount=time_slot.price,
            status='Pending'
        )

        logger.info("Razorpay order created: %s", razorpay_order['id'])

        # Return Razorpay order details for frontend payment processing
        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'amount': amount,
            'currency': 'INR',
            'booking_id': booking.id
        }, status=status.HTTP_201_CREATED)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from core.models import Booking
from automation.models import GoogleCredentials
from automation.utils import create_google_meet_event
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

class BookingStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, booking_id):
        # Get the booking
        booking = get_object_or_404(Booking, id=booking_id)

        # Ensure the mentor approving the booking is the one associated with the booking
        if booking.mentor.username.id != request.user.id:
            raise PermissionDenied("You do not have permission to modify this booking.")

        # Get new status and meeting link from the request data
        new_status = request.data.get('booking_status')
        meeting_link = request.data.get('meeting_link', None)

        # Validate the new status
        if new_status not in ['approved', 'rejected']:
            return Response({'error': 'Invalid booking status'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the meeting link only if the status is 'approved' and the link is provided
        if new_status == 'approved':
            if meeting_link:
                booking.meeting_link = meeting_link
            else:
                return Response({'error': 'Meeting link is required for approval.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the booking status and save
        booking.booking_status = new_status
        booking.save()

        return Response({'detail': f'Booking status updated to {new_status}.'}, status=status.HTTP_200_OK)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')
        booking_id = request.data.get('booking_id')

        logger.info(f"Payment verification initiated: payment_id={payment_id}, order_id={order_id}, signature={signature}, booking_id={booking_id}")

        # Ensure all required fields are present
        if not all([payment_id, order_id, signature, booking_id]):
            logger.error("Missing required payment details in request.")
            return Response({'error': 'Missing payment details.'}, status=status.HTTP_400_BAD_REQUEST)

        booking = get_object_or_404(Booking, id=booking_id)
        payment = get_object_or_404(Payment, booking=booking)
        amount_paid = booking.time_slot.price

        try:
            # Start transaction to ensure atomicity
            with transaction.atomic():
                # Verify the Razorpay payment
                if verify_payment(payment_id, order_id, signature):
                    # Update payment and booking status
                    booking.payment_status = True
                    booking.save()

                    payment.razorpay_payment_id = payment_id
                    payment.razorpay_signature = signature
                    payment.status = 'Success'
                    payment.amount = amount_paid
                    payment.save()

                    # Calculate commission and credit mentor’s wallet
                    commission_setting = CommissionSetting.objects.first()
                    commission = commission_setting.calculate_commission(amount_paid)
                    amount_to_credit = amount_paid - commission

                    # Update mentor’s wallet
                    mentor_wallet = Wallet.objects.get(user=booking.mentor.username)
                    mentor_wallet.balance += amount_to_credit
                    mentor_wallet.save()

                    WalletTransaction.objects.create(
                    wallet=mentor_wallet,
                    amount=amount_to_credit,
                    transaction_type="credit",
                    description=f"Mentorship Booking Made by {booking.mentee.first_name} {booking.mentee.last_name}"
                    )
                    # Log transaction in Paybook
                    PaybookEntry.objects.create(
                        booking=booking,
                        mentor=booking.mentor,
                        amount_paid=amount_paid,
                        commission_deducted=commission,
                        credited_to_wallet=amount_to_credit
                    )

                    logger.info(f"Payment verification successful for booking_id={booking_id}, payment_id={payment_id}.")
                    return Response({'status': 'Payment successful!'}, status=status.HTTP_200_OK)
                else:
                    logger.warning(f"Payment verification failed for booking_id={booking_id}, payment_id={payment_id}.")
                    payment.status = 'Failed'
                    payment.save()
                    return Response({'error': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during payment verification for booking_id={booking_id}: {str(e)}")
            return Response({'error': 'An error occurred during payment verification.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class ConvertToMentorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.user_type == 'mentee':
            user.convert_to_mentor()
            return Response({'message': 'User converted to mentor successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'User is already a mentor.'}, status=status.HTTP_400_BAD_REQUEST)

class LoggedInMentorDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            mentor = Mentor.objects.get(username=request.user)
            serializer = MentorSerializer(mentor)
            return Response(serializer.data)
        except Mentor.DoesNotExist:
            return Response({"error": "Mentor not found"}, status=404)

    def put(self, request):
        try:
            mentor = Mentor.objects.get(username=request.user)
            serializer = MentorSerializer(mentor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                print(serializer.errors)  # Add this line for debugging
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Mentor.DoesNotExist:
            return Response({"error": "Mentor not found"}, status=404)

class TimeBlockList(generics.ListAPIView):
    queryset = TimeBlock.objects.all()
    serializer_class = TimeBlockSerializer

class MentorTimeBlockListCreateView(generics.ListCreateAPIView):
    serializer_class = MentorTimeBlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        mentor = Mentor.objects.get(username=self.request.user)
        return MentorTimeBlock.objects.filter(mentor=mentor)

    def perform_create(self, serializer):
        mentor = Mentor.objects.get(username=self.request.user)
        time_block_id = self.request.data.get('time_block_id')
        price = self.request.data.get('price')

        # Log the data received for creating the time block
        logger.info(f"Received data for creating time block: time_block_id={time_block_id}, price={price}")

        time_block = get_object_or_404(TimeBlock, id=time_block_id)

        # Save the data and log the created object
        mentor_time_block = serializer.save(mentor=mentor, time_block=time_block, price=price)
        logger.info(f"Created MentorTimeBlock: {mentor_time_block}")

    def perform_update(self, serializer):
        mentor = Mentor.objects.get(username=self.request.user)

        # Log the data received for updating the time block
        logger.info(f"Received data for updating time block: {serializer.validated_data}")

        updated_time_block = serializer.save(mentor=mentor)
        
        # Log the updated object
        logger.info(f"Updated MentorTimeBlock: {updated_time_block}")

    def delete(self, request, *args, **kwargs):
        mentor = Mentor.objects.get(username=self.request.user)
        time_block_id = request.data.get('time_block_id')
        
        # Log the data received for deleting the time block
        logger.info(f"Received request to delete time block: time_block_id={time_block_id}")

        if not time_block_id:
            logger.error("Time Block ID is missing in the delete request")
            return Response({'error': 'Time Block ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        mentor_time_block = get_object_or_404(MentorTimeBlock, mentor=mentor, time_block_id=time_block_id)
        
        # Log the object before deletion
        logger.info(f"Deleting MentorTimeBlock: {mentor_time_block}")
        
        mentor_time_block.delete()
        
        # Log successful deletion
        logger.info(f"Successfully deleted MentorTimeBlock: time_block_id={time_block_id}")
        
        return Response(status=status.HTTP_204_NO_CONTENT)

class MenteeBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mentee = request.user  # Assuming mentee is authenticated
        bookings = Booking.objects.filter(mentee=mentee)  # Fetch bookings for the logged-in mentee
        serializer = MenteeBookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
class MenteeProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = MenteeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            # Use set() for updating interests
            interests = serializer.validated_data.pop('interests', None)
            if interests is not None:
                instance.interests.set(interests)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MentorBookingListView(ListAPIView):
    serializer_class = MentorBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Fetch only the bookings for the logged-in mentor
        mentor = self.request.user.mentor_profile
        return Booking.objects.filter(mentor=mentor).select_related('mentee', 'availability', 'time_slot')

class MenteeProfileDetailView(generics.RetrieveUpdateAPIView):  # Changed from RetrieveAPIView
    queryset = CustomUser.objects.filter(user_type='mentee')  # Only allow mentees
    serializer_class = MenteeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Fetch the authenticated user's profile
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Get the Google ID token from the frontend
        google_token = request.data.get("token")
        if not google_token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google
            id_info = id_token.verify_oauth2_token(google_token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            # Extract user info from the token
            email = id_info.get("email")
            first_name = id_info.get("given_name")
            last_name = id_info.get("family_name")
            username = email.split("@")[0]  # username is the part before '@'

            # Check if the user exists, else create a new user
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "user_type": "mentee",  # Default to mentee
                }
            )

            # Generate an authentication token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key,
                "user_id": user.id,
                "user_type": user.user_type,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            # Invalid token
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class UpdateableSuggestedMentorsView(APIView):
    """
    View to fetch all available interests, mentee's selected interests, 
    and suggested mentors based on mentee's interests.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Fetch mentee and their interests
        mentee = request.user
        interests = mentee.interests.all()

        # Get all available interests
        available_interests = Expertise.objects.all()
        interests_serializer = AvailableInterestsSerializer(
            available_interests, many=True, context={'mentee': mentee}
        )

        # Suggested mentors based on mentee's interests
        mentors = CustomUser.objects.filter(
            mentor_profile__expertise__in=interests
        ).distinct()
        mentor_serializer = MentorSerializer(mentors, many=True, context={'request': request})

        return Response({
            "available_interests": interests_serializer.data,
            "suggested_mentors": mentor_serializer.data
        }, status=200)

    def patch(self, request, *args, **kwargs):
        mentee = request.user
        updated_interests = request.data.get('interests', [])

        # Validate interests
        valid_interests = Expertise.objects.filter(id__in=updated_interests)
        if len(valid_interests) != len(updated_interests):
            return Response({'error': 'Invalid interests provided.'}, status=400)

        # Update mentee's interests
        mentee.interests.set(valid_interests)
        mentee.save()

        return Response({'message': 'Interests updated successfully.'}, status=200)

class MenteeInterestsView(APIView):
    """
    View to fetch and update mentee's interests.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        mentee = request.user
        available_interests = Expertise.objects.all()

        serializer = AvailableInterestsSerializer(
            available_interests, many=True, context={'mentee': mentee}
        )
        return Response(serializer.data, status=200)

    def patch(self, request, *args, **kwargs):
        mentee = request.user
        updated_interests = request.data.get('interests', [])

        # Validate interests
        valid_interests = Expertise.objects.filter(id__in=updated_interests)
        if len(valid_interests) != len(updated_interests):
            return Response({'error': 'Invalid interests provided.'}, status=400)

        # Update mentee's interests
        mentee.interests.set(valid_interests)
        mentee.save()

        return Response({'message': 'Interests updated successfully.'}, status=200)

class SuggestedMentorsView(generics.ListAPIView):
    """
    API to list suggested mentors based on mentee's interests.
    Allows mentee to view suggested mentors.
    """
    serializer_class = MentorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Fetch mentee's interests
        mentee = self.request.user
        interests = mentee.interests.all()

        # Fetch mentors with matching expertise
        if not interests.exists():
            return Mentor.objects.none()  # No mentors if no interests

        # Filter mentors based on matching expertise
        return Mentor.objects.filter(expertise__in=interests).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        interests = request.user.interests.all()

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "mentee_interests": [interest.name for interest in interests],
                "suggested_mentors": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class MentorAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get logged-in user
        user = request.user

        # Check if the user is a mentor
        try:
            mentor = user.mentor_profile
        except Mentor.DoesNotExist:
            return Response({"error": "You are not authorized to set availability."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve availability data
        availabilities = request.data.get('availabilities', [])

        if not availabilities:
            return Response({"error": "No availabilities provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Process each availability
        for availability in availabilities:
            date = availability.get('date')
            start_time = availability.get('start_time')
            end_time = availability.get('end_time')

            if not date or not start_time or not end_time:
                return Response({"error": "Invalid availability format."}, status=status.HTTP_400_BAD_REQUEST)

            # Check for conflicts
            conflicting = Availability.objects.filter(
                mentor=mentor,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if conflicting.exists():
                return Response(
                    {"error": f"Conflict detected for {date} {start_time}-{end_time}"},
                    status=status.HTTP_409_CONFLICT,
                )

            # Save availability
            Availability.objects.create(
                mentor=mentor,
                date=date,
                start_time=start_time,
                end_time=end_time
            )

        return Response({"message": "Availabilities set successfully."}, status=status.HTTP_201_CREATED)