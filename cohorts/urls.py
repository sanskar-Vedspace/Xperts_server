from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CohortViewSet, CohortRegistrationViewSet, PaymentViewSet, PaymentVerificationViewSet

router = DefaultRouter()
router.register(r'cohorts', CohortViewSet)
router.register(r'registrations', CohortRegistrationViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payment-verification/', PaymentVerificationViewSet.as_view({'post': 'create'})),
     path('cohorts/<slug:slug>/', CohortViewSet.as_view({'get': 'retrieve'}), name='cohort-detail-slug'),
]
