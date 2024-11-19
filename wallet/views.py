from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import datetime
import razorpay
import logging
from .models import Wallet, WalletTransaction
from core.models import Mentor, Availability, TimeSlot, Booking, Payment
from core.serializers import BookingSerializer
from .serializers import WalletSerializer, WalletTransactionSerializer
from django.conf import settings
from paybook.models import PaybookEntry,CommissionSetting
logger = logging.getLogger(__name__)

# Razorpay client initialization
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))


# Wallet Detail View - Get Wallet Balance
class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Add Funds to Wallet View
class AddFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a Razorpay order for wallet top-up
        razorpay_order = client.order.create({
            "amount": int(amount) * 100,  # Amount in paise
            "currency": "INR",
            "payment_capture": "1"
        })

        return Response({
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'amount': amount
        }, status=status.HTTP_201_CREATED)


# Verify Razorpay Payment and Update Wallet Balance
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get("razorpay_payment_id")
        order_id = request.data.get("razorpay_order_id")
        signature = request.data.get("razorpay_signature")
        bonus_amount = request.data.get("bonus_amount", 0)

        if not all([payment_id, order_id, signature]):
            logger.error("Missing payment details in request data.")
            return Response({"error": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify Razorpay payment signature
            params = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            is_valid = client.utility.verify_payment_signature(params)
            if not is_valid:
                return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve amount from the original order
            order = client.order.fetch(order_id)
            amount = Decimal(order.get("amount", 0)) / Decimal(100)

            # Update wallet balance
            wallet, created = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += amount
            wallet.save()

            # Add bonus amount if provided
            if Decimal(bonus_amount) > 0:
                wallet.balance += Decimal(bonus_amount)
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=Decimal(bonus_amount),
                    transaction_type="credit",
                    description="Bonus amount added"
                )

            # Log main transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=amount,
                transaction_type="credit",
                description="Funds added via Razorpay"
            )

            return Response({"status": "Payment successful and wallet updated"}, status=status.HTTP_200_OK)

        except razorpay.errors.SignatureVerificationError as e:
            return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("An error occurred during payment verification.")
            return Response({"error": "An error occurred during payment verification"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Transaction History View - View All Wallet Transactions
class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-created_at')
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response({'transactions': serializer.data}, status=status.HTTP_200_OK)


# Deduct Wallet Balance for Mentorship Booking
class DeductWalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            time_slot_id = request.data.get('time_slot_id')
            mentor_id = request.data.get('mentor_id')
            availability_id = request.data.get('availability_id')
            start_time_str = request.data.get('start_time')
            end_time_str = request.data.get('end_time')

            if not all([time_slot_id, mentor_id, availability_id, start_time_str, end_time_str]):
                return Response({'error': 'Required fields are missing.'}, status=status.HTTP_400_BAD_REQUEST)

            start_time = timezone.make_aware(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())
            end_time = timezone.make_aware(datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S'), timezone.get_current_timezone())

            time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
            amount_paid = time_slot.price
            wallet = Wallet.objects.get(user=request.user)

            if wallet.balance < amount_paid:
                return Response({'error': 'Insufficient wallet balance.'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Deduct balance and log transaction
                wallet.balance -= amount_paid
                wallet.save()
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount_paid,
                    transaction_type="debit",
                    description="Mentorship booking payment via wallet"
                )

                # Create booking
                mentor = get_object_or_404(Mentor, username_id=mentor_id)
                availability = get_object_or_404(Availability, id=availability_id)
                overlapping_bookings = Booking.objects.filter(
                    mentor=mentor,
                    availability=availability,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                    booking_status__in=['pending', 'approved']
                )
                if overlapping_bookings.exists():
                    return Response({"error": "The selected time slot is already booked."}, status=status.HTTP_409_CONFLICT)

                booking_data = {
                    'mentor': mentor,
                    'mentee': request.user,
                    'availability': availability,
                    'time_slot': time_slot,
                    'start_time': start_time,
                    'end_time': end_time,
                    'payment_status': True,
                    'wallet_payment_status': True
                }
                serializer = BookingSerializer(data=booking_data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                booking = serializer.save()

                # Calculate commission and credit mentor’s wallet
                commission_setting = CommissionSetting.objects.first()
                commission = commission_setting.calculate_commission(amount_paid)
                amount_to_credit = amount_paid - commission

                # Update mentor’s wallet
                mentor_wallet = Wallet.objects.get(user=mentor.username)
                mentor_wallet.balance += amount_to_credit
                mentor_wallet.save()
                WalletTransaction.objects.create(
                    wallet=mentor_wallet,
                    amount=amount_to_credit,
                    transaction_type="credit",
                    description=f"Mentorship Booking Made by {request.user.first_name} {request.user.last_name}"
                )
                # Log transaction in Paybook
                PaybookEntry.objects.create(
                    booking=booking,
                    mentor=mentor,
                    amount_paid=amount_paid,
                    commission_deducted=commission,
                    credited_to_wallet=amount_to_credit
                )

                # Create or update Payment record with amount explicitly set
                payment, created = Payment.objects.get_or_create(booking=booking, defaults={'amount': amount_paid})
                if not created:
                    payment.amount = amount_paid
                    payment.status = 'Success'
                    payment.save()

            return Response({
                "status": "Payment successful",
                "remaining_balance": wallet.balance,
                "booking_id": booking.id,
                "booking_details": serializer.data
            }, status=status.HTTP_200_OK)

        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred during wallet deduction and booking creation: {str(e)}", exc_info=True)
            return Response({"error": "An error occurred during wallet deduction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WalletPaymentVerificationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        logger.debug(f"Starting wallet payment verification for user {request.user.id}, booking_id {booking_id}")

        # Retrieve booking and wallet
        booking = get_object_or_404(Booking, id=booking_id)
        wallet = get_object_or_404(Wallet, user=request.user)

        # Get amount to deduct from wallet
        amount = booking.time_slot.price
        logger.debug(f"Amount to deduct: {amount}. Wallet balance: {wallet.balance}")

        # Check sufficient wallet balance
        if wallet.balance < amount:
            logger.warning(f"Insufficient wallet balance. Required: {amount}, Available: {wallet.balance}")
            return Response({"error": "Insufficient wallet balance."}, status=status.HTTP_400_BAD_REQUEST)

        # Deduct balance within a transaction
        try:
            with transaction.atomic():
                # Deduct wallet balance and log transaction
                wallet.balance -= amount
                wallet.save()
                logger.info(f"Deducted {amount} from wallet for user {request.user.id}. New balance: {wallet.balance}")

                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type="debit",
                    description="Mentorship booking payment via wallet"
                )
                logger.debug("Wallet transaction recorded.")

                # Update booking statuses to reflect wallet payment
                booking.payment_status = True
                booking.wallet_payment_status = True
                booking.save()
                logger.info(f"Booking {booking.id} updated with payment_status=True and wallet_payment_status=True")

                # Update payment status or create a new Payment record if it doesn't exist
                payment, created = Payment.objects.get_or_create(booking=booking)
                payment.status = "Success"
                payment.amount = amount  # Ensure amount is set here
                payment.save()
                logger.debug(f"Payment status set to Success for booking {booking.id}")

        except Exception as e:
            logger.error(f"Error during wallet payment processing: {e}")
            return Response({"error": "Failed to process wallet payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Confirm status update by refreshing from the database
        booking.refresh_from_db()
        if booking.payment_status and booking.wallet_payment_status:
            logger.info(f"Booking {booking.id} successfully marked as paid with wallet.")
        else:
            logger.error(f"Booking {booking.id} did not reflect payment status changes as expected.")

        return Response({
            "status": "Wallet payment successful",
            "booking_id": booking.id,
            "remaining_balance": wallet.balance
        }, status=status.HTTP_200_OK)