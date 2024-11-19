from django.urls import path, include
from .views import CheckUsernameView,CheckEmailView,VerifyOTPView,MentorAvailabilityView,CreateBookingView,MenteeInterestsView,SuggestedMentorsView,GoogleLoginView,VerifyPaymentView, RegisterView, LoginView, MentorList, MentorDetail, MentorProfileView, ConvertToMentorView, LoggedInMentorDetailView, TimeBlockList, UserProfileView, MentorTimeBlockListCreateView, MentorAvailableSlotsView,MenteeBookingView,MenteeProfileView,MentorBookingListView,MenteeProfileDetailView,BookingStatusUpdateView,UpdateableSuggestedMentorsView

urlpatterns = [
    path('auth/google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('mentors/', MentorList.as_view(), name='mentor-list'),
    path('mentors/<int:pk>/', MentorDetail.as_view(), name='mentor-detail'),
    path('mentors/me/', LoggedInMentorDetailView.as_view(), name='logged-in-mentor-detail'),
    path('mentors/<str:username>/', MentorProfileView.as_view(), name='mentor-profile'),
    path('time-blocks/', TimeBlockList.as_view(), name='time-block-list'),
    path('users/<int:pk>/', UserProfileView.as_view(), name='user-profile'),
    path('convert-to-mentor/', ConvertToMentorView.as_view(), name='convert-to-mentor'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('check-username/', CheckUsernameView.as_view(), name='check-username'),
    path('check-email/', CheckEmailView.as_view(), name='check-email'),
    path('mentors/<int:mentor_id>/available-slots/', MentorAvailableSlotsView.as_view(), name='mentor-available-slots'),
    path('mentorbooking/create-booking/', CreateBookingView.as_view(), name='create-booking'),
    path('mentorbooking/verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('mentee-bookings/', MenteeBookingView.as_view(), name='mentee-bookings'),
    path('mentee-profile/', MenteeProfileView.as_view(), name='mentee-profile'),
    path('mentor-time-blocks/', MentorTimeBlockListCreateView.as_view(), name='mentor-time-block-list-create'),
    path('user-profile/', MenteeProfileView.as_view(), name='user-profile'),
    path('mentee-profile/<int:pk>/', MenteeProfileDetailView.as_view(), name='mentee-profile-detail'),
    path('mentor/bookings/', MentorBookingListView.as_view(), name='mentor-booking-list'),
    path('booking-status/<int:booking_id>/', BookingStatusUpdateView.as_view(), name='booking-status-update'),
    path('mentee/suggested-mentors/', UpdateableSuggestedMentorsView.as_view(), name='suggested-mentors'),
    path('mentee/interests/', MenteeInterestsView.as_view(), name='mentee-interests'),
    path('mentee/suggested-mentors-list/', SuggestedMentorsView.as_view(), name='suggested-mentors-list'),
    path('mentor/availability/', MentorAvailabilityView.as_view(), name='mentor-availability'),

]


