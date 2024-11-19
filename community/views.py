import razorpay
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from industry.models import Expertise
from .models import SubscriptionPlan, Subscription, SubscriptionPayment, Post, Group, Like, Comment, Share, Follow
from .serializers import (
    SubscriptionPlanSerializer, SubscriptionSerializer, SubscriptionPaymentSerializer,
    PostSerializer, GroupSerializer, LikeSerializer, CommentSerializer, ShareSerializer, FollowSerializer
)
from django.shortcuts import get_object_or_404
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)
# Razorpay client initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

class CreateRazorpayOrderView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        plan_id = request.data.get('plan_id')

        # Fetch the subscription plan
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)

        # Create a subscription
        subscription = Subscription.objects.create(user=user, plan=plan, is_active=False)

        # Create Razorpay order
        order_amount = int(plan.price * 100)  # Razorpay takes amount in paise
        order_currency = 'INR'

        razorpay_order = razorpay_client.order.create({
            'amount': order_amount,
            'currency': order_currency,
            'payment_capture': '1'
        })

        # Save the order ID in the payment model
        payment = SubscriptionPayment.objects.create(
            subscription=subscription,
            amount=plan.price,
            razorpay_order_id=razorpay_order['id'],
        )

        # Return the order details to the frontend for payment
        return Response({
            'order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_API_KEY,
            'amount': order_amount,
            'currency': order_currency,
            'subscription_id': subscription.id,
        }, status=status.HTTP_201_CREATED)


class VerifyRazorpayPaymentView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        subscription_id = request.data.get('subscription_id')

        # Fetch the subscription and payment details
        subscription = get_object_or_404(Subscription, id=subscription_id)
        payment = get_object_or_404(SubscriptionPayment, subscription=subscription, razorpay_order_id=razorpay_order_id)

        # Verify the payment signature
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Update payment and subscription details
            payment.transaction_id = razorpay_payment_id
            payment.save()

            subscription.is_active = True
            subscription.save()

            return Response({'status': 'Payment verified successfully!'}, status=status.HTTP_200_OK)

        except razorpay.errors.SignatureVerificationError:
            return Response({'error': 'Payment verification failed!'}, status=status.HTTP_400_BAD_REQUEST)


class GroupListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'mentor':
            user_expertise = user.mentor_profile.expertise.all()
        else:
            user_expertise = user.interests.all()  # Mentees have interests
        return Group.objects.filter(expertise__in=user_expertise)

    def get_serializer_context(self):
        # Ensure that 'request' is passed to the serializer context
        context = super(GroupListView, self).get_serializer_context()
        context.update({"request": self.request})
        return context


class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Fetch group and expertise based on provided IDs
        group = get_object_or_404(Group, id=self.request.data.get('group_id'))
        expertise = get_object_or_404(Expertise, id=self.request.data.get('expertise_id'))
        
        # Additional data handling based on content type
        content_type = self.request.data.get('content_type')
        
        # Process and save the data based on content type
        serializer.save(
            author=self.request.user,
            group=group,
            expertise=expertise,
            content_type=content_type,
            content=self.request.data.get('content'),
            image=self.request.FILES.get('image') if content_type == 'image' else None,
            document=self.request.FILES.get('document') if content_type == 'document' else None,
            pdf=self.request.FILES.get('pdf') if content_type == 'pdf' else None,
            poll_options=self.request.data.get('poll_options') if content_type == 'poll' else None
        )

    def get_queryset(self):
        return Post.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


# views.py
class LikePostView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        user = request.user

        # Check if the user has already liked the post
        existing_like = Like.objects.filter(post=post, user=user).first()

        if existing_like:
            # Unlike the post (remove the like)
            existing_like.delete()
            message = 'Like removed.'
            is_liked = False
        else:
            # Like the post (create a new like)
            Like.objects.create(user=user, post=post)
            message = 'Post liked.'
            is_liked = True

        # Update the like count after the action
        likes_count = post.likes.count()

        # Broadcast the like/unlike action via WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "like_updates",  # Ensure this matches with your consumer
            {
                'type': 'like_update',
                'post_id': post.id,
                'likes_count': likes_count,
                'is_liked': is_liked,
            }
        )

        return Response({'message': message, 'is_liked': is_liked, 'likes_count': likes_count})



class CommentPostView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        logger.info(f"Received Comment request - User: {self.request.user}, Post ID: {post.id}")

        # Log the incoming data from the frontend (for debugging)
        logger.debug(f"Incoming data from frontend (Comment): {self.request.data}")

        if serializer.is_valid():
            serializer.save(user=self.request.user, post=post)
            logger.info(f"Comment saved successfully - User: {self.request.user}, Post ID: {post.id}")
        else:
            logger.error(f"Comment serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SharePostView(generics.CreateAPIView):
    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        serializer.save(user=self.request.user, post=post)


class FollowMentorView(generics.CreateAPIView):
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        mentor = get_object_or_404(settings.AUTH_USER_MODEL, id=self.kwargs['mentor_id'])
        serializer.save(follower=self.request.user, followed=mentor)
