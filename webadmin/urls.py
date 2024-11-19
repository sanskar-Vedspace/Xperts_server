from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomepageViewSet, AboutPageViewSet, ContactPageViewSet, PrivacyPolicyPageViewSet, NewsletterPageViewSet, CustomPageViewSet
from .views import MentoringCTAViewSet,MenttalkCTAViewSet
from .views import FooterViewSet

router = DefaultRouter()
router.register(r'mentoringcta', MentoringCTAViewSet)
router.register(r'menttalkcta', MenttalkCTAViewSet, basename='menttalkcta')
router.register(r'home', HomepageViewSet)
router.register(r'about', AboutPageViewSet)
router.register(r'contact', ContactPageViewSet)
router.register(r'privacy', PrivacyPolicyPageViewSet)
router.register(r'newsletter', NewsletterPageViewSet)
router.register(r'custom-pages', CustomPageViewSet)
router.register(r'footer', FooterViewSet, basename='footer')

urlpatterns = [
    path('', include(router.urls)),
]
