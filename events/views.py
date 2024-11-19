from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Event, EventRegistration, EventPayment
from .serializers import EventSerializer, EventRegistrationSerializer, EventPaymentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from razorpay import Client
from django.conf import settings
from django.utils.crypto import hmac
import hashlib
import logging
from rest_framework.views import APIView

# Get an instance of a logger
logger = logging.getLogger('events')
# Initialize the Razorpay client with your API key and secret
razorpay_client = Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]


class EventPaymentViewSet(viewsets.ModelViewSet):
    queryset = EventPayment.objects.all()
    serializer_class = EventPaymentSerializer

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        logger.debug(f"Updating payment with ID: {payment.id}")

        try:
            # Store the Razorpay details including the signature
            payment.razorpay_payment_id = request.data.get('razorpay_payment_id')
            payment.razorpay_signature = request.data.get('razorpay_signature')
            payment.payment_status = 'Success' if request.data.get('status') == 'Success' else 'Failed'
            payment.save()

            logger.info(f"Payment {payment.id} updated successfully")

            if payment.payment_status == 'Success':
                payment.event_registration.payment_status = 'Completed'
                payment.event_registration.save()

                logger.info(f"Registration {payment.event_registration.id} marked as completed")

            return Response({"status": "Payment status updated and signature stored."})

        except Exception as e:
            logger.error(f"Failed to update payment: {str(e)}")
            return Response({"status": "Failed to update payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer

    def create(self, request, *args, **kwargs):
        logger.debug("Creating a new event registration")
        event = Event.objects.get(id=request.data.get('event'))
        user = request.user

        existing_registration = EventRegistration.objects.filter(event=event, user=user).first()
        if existing_registration:
            logger.warning(f"User {user.id} has already registered for event {event.id}")
            return Response({"detail": "You have already registered for this event."}, status=status.HTTP_400_BAD_REQUEST)

        registration = EventRegistration.objects.create(
            user=user,
            event=event,
            payment_status='Pending'
        )
        logger.info(f"Event registration created with ID: {registration.id}")

        # Create a Razorpay order
        try:
            razorpay_order = razorpay_client.order.create({
                "amount": int(event.price * 100),  # Amount in paisa
                "currency": "INR",
                "receipt": str(registration.id),
                "payment_capture": 1
            })
            logger.debug(f"Razorpay order created with ID: {razorpay_order['id']}")

            payment = EventPayment.objects.create(
                user=user,
                event_registration=registration,
                amount=event.price,
                razorpay_order_id=razorpay_order['id']
            )
            logger.info(f"Payment created with ID: {payment.id}")

            return Response({
                "registration_id": registration.id,
                "razorpay_order_id": razorpay_order['id'],
                "amount": event.price
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {str(e)}")
            return Response({"detail": "Failed to create Razorpay order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class EventPaymentVerificationViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')

        payment = EventPayment.objects.get(razorpay_order_id=order_id)

        # Generate the signature using the payment details
        generated_signature = hmac.new(
            key=settings.RAZORPAY_API_SECRET.encode(),
            msg=(order_id + "|" + payment_id).encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        if generated_signature == signature:
            payment.verified = True
            payment.payment_status = 'Success'
            payment.event_registration.payment_status = 'Completed'
            payment.event_registration.save()
            payment.save()

            return Response({"status": "Payment verified and registration completed."}, status=status.HTTP_200_OK)
        else:
            payment.payment_status = 'Failed'
            payment.save()
            return Response({"status": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

class MenteeRegisteredEventsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the logged-in user (mentee)
        registrations = EventRegistration.objects.filter(user=user)  # Fetch all events the user has registered for
        serializer = EventRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)