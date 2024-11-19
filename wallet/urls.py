from django.urls import path
from .views import WalletDetailView, AddFundsView, VerifyPaymentView, TransactionHistoryView,DeductWalletBalanceView

urlpatterns = [
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallet/add-funds/', AddFundsView.as_view(), name='add-funds'),
    path('wallet/verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('wallet/transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('wallet/deduct/', DeductWalletBalanceView.as_view(), name='deduct-wallet-balance'),
]
