# utils.py

from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import status
from core.models import Booking, Payment
from .models import Wallet, WalletTransaction
import logging

logger = logging.getLogger('wallet')

def verify_wallet_payment(user, booking_id):
    """
    Verifies wallet payment for a given booking by deducting wallet balance
    and updating booking and payment statuses.
    """
    logger.debug(f"Starting wallet payment verification for user {user.id}, booking_id {booking_id}")

    # Retrieve booking and wallet
    booking = get_object_or_404(Booking, id=booking_id)
    wallet = get_object_or_404(Wallet, user=user)

    # Get amount to deduct from wallet
    amount = booking.time_slot.price
    logger.debug(f"Amount to deduct: {amount}. Wallet balance: {wallet.balance}")

    # Check sufficient wallet balance
    if wallet.balance < amount:
        logger.warning(f"Insufficient wallet balance. Required: {amount}, Available: {wallet.balance}")
        return {"error": "Insufficient wallet balance.", "status": status.HTTP_400_BAD_REQUEST}

    # Deduct balance within a transaction
    try:
        with transaction.atomic():
            # Deduct wallet balance and log transaction
            wallet.balance -= amount
            wallet.save()
            logger.info(f"Deducted {amount} from wallet for user {user.id}. New balance: {wallet.balance}")

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
            payment.save()
            logger.debug(f"Payment status set to Success for booking {booking.id}")

    except Exception as e:
        logger.error(f"Error during wallet payment processing: {e}")
        return {"error": "Failed to process wallet payment", "status": status.HTTP_500_INTERNAL_SERVER_ERROR}

    # Confirm status update by refreshing from the database
    booking.refresh_from_db()
    if booking.payment_status and booking.wallet_payment_status:
        logger.info(f"Booking {booking.id} successfully marked as paid with wallet.")
    else:
        logger.error(f"Booking {booking.id} did not reflect payment status changes as expected.")

    return {"status": "success"}
