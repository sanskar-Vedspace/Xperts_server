import hmac
import hashlib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def verify_payment(razorpay_payment_id, razorpay_order_id, razorpay_signature):
    """
    Verifies the Razorpay payment signature manually using HMAC with SHA-256.
    
    :param razorpay_payment_id: The Razorpay Payment ID
    :param razorpay_order_id: The Razorpay Order ID
    :param razorpay_signature: The Razorpay Signature from the response
    :return: True if verification is successful, False otherwise
    """
    try:
        # Construct the expected signature message
        message = f"{razorpay_order_id}|{razorpay_payment_id}"

        # Create the HMAC SHA-256 signature using the Razorpay secret key
        secret = settings.RAZORPAY_API_SECRET.encode('utf-8')
        generated_signature = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).hexdigest()

        logger.info("Generated HMAC signature: %s", generated_signature)

        # Compare the generated signature with the received signature
        if hmac.compare_digest(generated_signature, razorpay_signature):
            logger.info("HMAC Signature Verification successful")
            return True
        else:
            logger.error("HMAC Signature Verification failed")
            return False

    except Exception as e:
        # Log any errors during the process
        logger.error("Error during HMAC verification: %s", str(e))
        return False
