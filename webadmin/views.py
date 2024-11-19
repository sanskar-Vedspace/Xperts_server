from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Homepage, AboutPage, ContactPage, PrivacyPolicyPage, NewsletterPage, CustomPage, MentoringCTA
from .serializers import HomepageSerializer, AboutPageSerializer, ContactPageSerializer, PrivacyPolicyPageSerializer, NewsletterPageSerializer, CustomPageSerializer, MentoringCTASerializer
from .models import MenttalkCTA
from .serializers import MenttalkCTASerializer
from .models import Footer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import FooterSerializer
from rest_framework.decorators import action
from rest_framework import status

class FooterViewSet(viewsets.ModelViewSet):
    queryset = Footer.objects.all()
    serializer_class = FooterSerializer
    permission_classes = [AllowAny] 
    @action(detail=False, methods=['get'])
    def get_footer(self, request, *args, **kwargs):
        """
        Since Footer is a singleton model, 
        we override this method to always return the first (and only) Footer object.
        """
        footer = Footer.objects.first()
        if not footer:
            return Response({"error": "Footer not found"}, status=404)

        serializer = self.get_serializer(footer)
        return Response(serializer.data)

class MenttalkCTAViewSet(viewsets.ModelViewSet):
    queryset = MenttalkCTA.objects.all()
    serializer_class = MenttalkCTASerializer
    http_method_names = ['get', 'put', 'patch']  # Limit the methods to only 'get', 'put', and 'patch' (no delete or post)

    def get_permissions(self):
        # Allow any user to access the GET method
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

class MentoringCTAViewSet(viewsets.ModelViewSet):
    queryset = MentoringCTA.objects.all()
    serializer_class = MentoringCTASerializer
    http_method_names = ['get', 'put', 'patch']
    def get_permissions(self):
        if self.request.method in ['GET']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class HomepageViewSet(viewsets.ModelViewSet):
    queryset = Homepage.objects.all()
    serializer_class = HomepageSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method in ['GET']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

class AboutPageViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing AboutPage instances.
    """
    queryset = AboutPage.objects.all()
    serializer_class = AboutPageSerializer
    permission_classes = [AllowAny]

    # Override the list method to return the singleton instance
    def list(self, request, *args, **kwargs):
        try:
            about_page = AboutPage.objects.get()
            serializer = self.get_serializer(about_page)
            return Response(serializer.data)
        except AboutPage.DoesNotExist:
            return Response({"error": "About page not found"}, status=status.HTTP_404_NOT_FOUND)

    # Optionally override the retrieve method to get the singleton instance by its ID
    def retrieve(self, request, *args, **kwargs):
        try:
            about_page = AboutPage.objects.get()
            serializer = self.get_serializer(about_page)
            return Response(serializer.data)
        except AboutPage.DoesNotExist:
            return Response({"error": "About page not found"}, status=status.HTTP_404_NOT_FOUND)

    # Optionally add a custom action to get the about page without needing an ID in the URL
    @action(detail=False, methods=['get'])
    def get_about(self, request):
        try:
            about_page = AboutPage.objects.get()
            serializer = self.get_serializer(about_page)
            return Response(serializer.data)
        except AboutPage.DoesNotExist:
            return Response({"error": "About page not found"}, status=status.HTTP_404_NOT_FOUND)

class ContactPageViewSet(viewsets.ModelViewSet):
    queryset = ContactPage.objects.all()
    serializer_class = ContactPageSerializer
    permission_classes = [AllowAny]

class PrivacyPolicyPageViewSet(viewsets.ModelViewSet):
    queryset = PrivacyPolicyPage.objects.all()
    serializer_class = PrivacyPolicyPageSerializer
    permission_classes = [AllowAny]

class NewsletterPageViewSet(viewsets.ModelViewSet):
    queryset = NewsletterPage.objects.all()
    serializer_class = NewsletterPageSerializer
    permission_classes = [AllowAny]

class CustomPageViewSet(viewsets.ModelViewSet):
    queryset = CustomPage.objects.all()
    serializer_class = CustomPageSerializer
    permission_classes = [AllowAny]
