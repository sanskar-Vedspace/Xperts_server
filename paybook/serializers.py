from rest_framework import serializers
from .models import PaybookEntry, CommissionSetting,PayoutRequest

class PaybookEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaybookEntry
        fields = ['booking', 'mentor', 'amount_paid', 'commission_deducted', 'credited_to_wallet', 'created_at']

class CommissionSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionSetting
        fields = ['commission_type', 'commission_value', 'minimum_payout']
class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutRequest
        fields = ['id', 'mentor', 'amount', 'status', 'requested_at', 'processed_at']