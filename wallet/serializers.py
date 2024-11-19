from rest_framework import serializers
from .models import Wallet, WalletTransaction

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'balance']
        read_only_fields = ['user']  # Make user read-only since it should be auto-assigned

class WalletTransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.CharField(source='get_transaction_type_display')  # If using choices for types

    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'amount', 'description', 'created_at']
        read_only_fields = ['id', 'transaction_type', 'amount', 'description', 'created_at']
