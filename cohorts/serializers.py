from rest_framework import serializers
from .models import Cohort, CohortRegistration, Payment

class CohortSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Cohort
        fields = '__all__'  # Ensure slug is included in all fields

    def get_participants(self, obj):
        return obj.participants


class CohortRegistrationSerializer(serializers.ModelSerializer):
    cohort_name = serializers.CharField(source='cohort.name', read_only=True)
    mentor_name = serializers.CharField(source='cohort.mentor.username', read_only=True)

    class Meta:
        model = CohortRegistration
        fields = [
            'id', 
            'user', 
            'cohort', 
            'cohort_name', 
            'mentor_name', 
            'registered_at', 
            'payment_status'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    cohort_name = serializers.CharField(source='cohort_registration.cohort.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 
            'user', 
            'user_name', 
            'cohort_registration', 
            'cohort_name', 
            'amount', 
            'payment_date', 
            'payment_status', 
            'razorpay_order_id', 
            'razorpay_payment_id', 
            'razorpay_signature', 
            'verified'  # Include the verification status field
        ]
        read_only_fields = ['payment_date', 'verified']  # Make certain fields read-only
