from rest_framework import generics
from .models import Expertise
from .serializers import ExpertiseSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny

class ExpertiseListView(generics.ListAPIView):
    queryset = Expertise.objects.all()
    serializer_class = ExpertiseSerializer
    permission_classes = [AllowAny]