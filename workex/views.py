from rest_framework import generics
from .models import WorkExperience
from .serializers import WorkExperienceSerializer
from rest_framework.permissions import IsAuthenticated

class WorkExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WorkExperience.objects.filter(mentor=self.request.user.mentor_profile)

    def perform_create(self, serializer):
        serializer.save(mentor=self.request.user.mentor_profile)
