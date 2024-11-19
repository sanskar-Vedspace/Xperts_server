from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventRegistrationViewSet, EventPaymentViewSet, EventPaymentVerificationViewSet,MenteeRegisteredEventsView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'event-registrations', EventRegistrationViewSet)
router.register(r'event-payments', EventPaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),  # Include the router for all default routes
    path('events/<slug:slug>/', EventViewSet.as_view({'get': 'retrieve'}), name='event-detail-slug'),  # Slug-based path
    path('event-payment-verification/', EventPaymentVerificationViewSet.as_view({'post': 'create'})),
    path('mentee/events/', MenteeRegisteredEventsView.as_view(), name='mentee-registered-events'),
]
