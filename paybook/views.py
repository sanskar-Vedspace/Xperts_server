from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import PaybookEntry, CommissionSetting,PayoutRequest
from wallet.models import WalletTransaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from .serializers import PaybookEntrySerializer, CommissionSettingSerializer,PayoutRequestSerializer
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

class CommissionSettingView(generics.RetrieveUpdateAPIView):
    queryset = CommissionSetting.objects.all()
    serializer_class = CommissionSettingSerializer
    permission_classes = [IsAuthenticated]  

    def get_object(self):
        return CommissionSetting.objects.first()

class PaybookEntryListView(generics.ListAPIView):
    queryset = PaybookEntry.objects.all()
    serializer_class = PaybookEntrySerializer
    permission_classes = [IsAdminUser]

class PayoutRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mentor = request.user.mentor_profile  # Ensure user is a mentor
        amount = Decimal(request.data.get('amount'))
        
        # Get the minimum payout amount
        commission_setting = CommissionSetting.objects.first()
        if not commission_setting:
            return Response({'error': 'Payout settings not configured.'}, status=400)
        
        min_payout = commission_setting.minimum_payout
        wallet = mentor.username.wallet

        if amount < min_payout:
            return Response({'error': f'Minimum payout amount is {min_payout}.'}, status=400)
        
        if wallet.balance < amount:
            return Response({'error': 'Insufficient wallet balance.'}, status=400)

        # Deduct amount and create payout request
        wallet.balance -= amount
        wallet.save()
        
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type='debit',
            description='Payout Request'
        )

        payout_request = PayoutRequest.objects.create(
            mentor=mentor,
            amount=amount,
            status='pending'
        )

        return Response({'status': 'Payout request created successfully.', 'payout_request': payout_request.id})

    def get(self, request):
        mentor = request.user.mentor_profile
        payout_requests = PayoutRequest.objects.filter(mentor=mentor)
        serializer = PayoutRequestSerializer(payout_requests, many=True)
        return Response(serializer.data)

class ApprovePayoutRequestView(APIView):
    permission_classes = [IsAdminUser]  # Limit this to admin users

    def post(self, request, payout_request_id):
        payout_request = PayoutRequest.objects.get(id=payout_request_id)

        if payout_request.status != 'pending':
            return Response({'error': 'Payout request has already been processed.'}, status=400)

        action = request.data.get('action')  # 'approve' or 'reject'
        if action == 'approve':
            payout_request.status = 'approved'
            payout_request.processed_at = now()
            payout_request.save()
            return Response({'status': 'Payout request approved.'})
        elif action == 'reject':
            # Refund amount to mentor's wallet
            wallet = payout_request.mentor.username.wallet
            wallet.balance += payout_request.amount  # Add the payout amount back to the wallet
            wallet.save()

            # Create a wallet transaction to log the refund
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=payout_request.amount,
                transaction_type='credit',
                description='Payout Rejection Refund'
            )

            # Update payout request status
            payout_request.status = 'rejected'
            payout_request.processed_at = now()
            payout_request.save()

            return Response({'status': 'Payout request rejected and amount refunded.'})