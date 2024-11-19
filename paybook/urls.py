from django.urls import path
from .views import PaybookEntryListView, CommissionSettingView,PayoutRequestView,ApprovePayoutRequestView

urlpatterns = [
    path('paybook/', PaybookEntryListView.as_view(), name='paybook-list'),
    path('paybook/commission-setting/', CommissionSettingView.as_view(), name='commission-setting'),
    path('payout-request/', PayoutRequestView.as_view(), name='payout-request'),
    path('payout-request/<int:payout_request_id>/approve/', ApprovePayoutRequestView.as_view(), name='approve-payout-request'),
]
