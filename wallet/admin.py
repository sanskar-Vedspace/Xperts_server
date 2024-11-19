from django.contrib import admin
from .models import Wallet, WalletTransaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')  # Display the user and balance in the list view
    search_fields = ('user__username',)  # Enable search by username
    readonly_fields = ('balance',)  # Make the balance field read-only in the admin

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'created_at', 'description')
    list_filter = ('transaction_type',)  # Enable filtering by transaction type (credit/debit)
    search_fields = ('wallet__user__username', 'description')  # Search by username and description
    readonly_fields = ('wallet', 'transaction_type', 'amount', 'created_at', 'description')  # Make fields read-only
