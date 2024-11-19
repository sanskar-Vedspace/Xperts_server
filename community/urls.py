from django.urls import path
from .views import CreateRazorpayOrderView, VerifyRazorpayPaymentView, GroupListView, PostListCreateView, LikePostView, CommentPostView, SharePostView, FollowMentorView

urlpatterns = [
    path('create-order/', CreateRazorpayOrderView.as_view(), name='create-razorpay-order'),
    path('verify-payment/', VerifyRazorpayPaymentView.as_view(), name='verify-razorpay-payment'),
    path('groups/', GroupListView.as_view(), name='group-list'),
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/comment/', CommentPostView.as_view(), name='comment-post'),
    path('posts/<int:post_id>/share/', SharePostView.as_view(), name='share-post'),
    path('mentors/<int:mentor_id>/follow/', FollowMentorView.as_view(), name='follow-mentor'),
]
