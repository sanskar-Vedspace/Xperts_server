# tools/views.py
from rest_framework import generics
from .models import Tool
from .serializers import ToolSerializer
from rest_framework.permissions import IsAuthenticated

class ToolListView(generics.ListAPIView):
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    permission_classes = [IsAuthenticated]
