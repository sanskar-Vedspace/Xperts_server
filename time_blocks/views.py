from rest_framework import generics
from .models import TimeBlock
from .serializers import TimeBlockSerializer

class TimeBlockListView(generics.ListCreateAPIView):
    queryset = TimeBlock.objects.all()
    serializer_class = TimeBlockSerializer

class TimeBlockDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeBlock.objects.all()
    serializer_class = TimeBlockSerializer
