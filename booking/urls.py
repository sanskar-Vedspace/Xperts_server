from django.urls import path
from .views import CreateBookingView, VerifyPaymentView

urlpatterns = [
    path('create-booking/', CreateBookingView.as_view(), name='create-booking'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),
]
