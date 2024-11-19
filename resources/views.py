from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Resource
from .serializers import ResourceSerializer

class ResourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [AllowAny]  # This allows unrestricted access to this view
