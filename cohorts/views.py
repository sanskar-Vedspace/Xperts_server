from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Cohort, CohortRegistration, Payment
from .serializers import CohortSerializer, CohortRegistrationSerializer, PaymentSerializer
from django.utils.crypto import hmac
from razorpay import Client
from django.conf import settings
import hashlib
import logging

# Initialize logger
logger = logging.getLogger('cohorts')

# Initialize Razorpay client
razorpay_client = Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
    lookup_field = 'slug' 
    
    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get('slug')  # Capture 'slug' from kwargs
        logger.debug(f"Slug received in view: {slug}")
        if slug:
            cohort = get_object_or_404(Cohort, slug=slug)  # Look up cohort by slug
            serializer = self.get_serializer(cohort)
            return Response(serializer.data)
        return super().retrieve(request, *args, **kwargs)



class CohortRegistrationViewSet(viewsets.ModelViewSet):
    queryset = CohortRegistration.objects.all()
    serializer_class = CohortRegistrationSerializer

    def create(self, request, *args, **kwargs):
        logger.debug("Creating a new cohort registration")
        cohort = get_object_or_404(Cohort, id=request.data.get('cohort'))
        user = request.user

        existing_registration = CohortRegistration.objects.filter(cohort=cohort, user=user).first()
        if existing_registration:
            logger.warning(f"User {user.id} already registered for cohort {cohort.id}")
            return Response({"detail": "You are already registered for this cohort."}, status=status.HTTP_400_BAD_REQUEST)

        registration = CohortRegistration.objects.create(
            user=user,
            cohort=cohort,
            payment_status='Pending'
        )
        logger.info(f"Cohort registration created with ID: {registration.id}")

        try:
            razorpay_order = razorpay_client.order.create({
                "amount": int(cohort.price * 100),  # Amount in paisa
                "currency": "INR",
                "receipt": str(registration.id),
                "payment_capture": 1
            })
            logger.debug(f"Razorpay order created with ID: {razorpay_order['id']}")

            payment = Payment.objects.create(
                user=user,
                cohort_registration=registration,
                amount=cohort.price,
                razorpay_order_id=razorpay_order['id']
            )
            logger.info(f"Payment created with ID: {payment.id}")

            return Response({
                "registration_id": registration.id,
                "razorpay_order_id": razorpay_order['id'],
                "amount": cohort.price
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to create Razorpay order: {str(e)}")
            return Response({"detail": "Failed to create Razorpay order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        logger.debug(f"Updating payment with ID: {payment.id}")

        try:
            payment.razorpay_payment_id = request.data.get('razorpay_payment_id')
            payment.razorpay_signature = request.data.get('razorpay_signature')
            payment.payment_status = 'Success' if request.data.get('status') == 'Success' else 'Failed'
            payment.save()

            if payment.payment_status == 'Success':
                payment.cohort_registration.payment_status = 'Completed'
                payment.cohort_registration.save()

            logger.info(f"Payment {payment.id} updated successfully")
            return Response({"status": "Payment status updated and signature stored."})
        except Exception as e:
            logger.error(f"Failed to update payment: {str(e)}")
            return Response({"status": "Failed to update payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerificationViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')

        payment = Payment.objects.get(razorpay_order_id=order_id)

        generated_signature = hmac.new(
            key=settings.RAZORPAY_API_SECRET.encode(),
            msg=(order_id + "|" + payment_id).encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        if generated_signature == signature:
            payment.verified = True
            payment.payment_status = 'Success'
            payment.cohort_registration.payment_status = 'Completed'
            payment.cohort_registration.save()
            payment.save()

            return Response({"status": "Payment verified and registration completed."}, status=status.HTTP_200_OK)
        else:
            payment.payment_status = 'Failed'
            payment.save()
            return Response({"status": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)


class MenteeRegisteredCohortsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        registrations = CohortRegistration.objects.filter(user=user)
        serializer = CohortRegistrationSerializer(registrations, many=True)
        return Response(serializer.data)
