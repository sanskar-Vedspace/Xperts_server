import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def create_razorpay_order(booking):
    """
    Create Razorpay order for the given booking
    """
    order_amount = int(booking.time_slot.price * 100)  # Razorpay accepts the amount in paise
    order_currency = 'INR'
    order_receipt = f'booking_{booking.id}'

    razorpay_order = razorpay_client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': '1'
    })

    return razorpay_order

def verify_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature):
    """
    Verify Razorpay payment
    """
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_signature': razorpay_signature
        })
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
