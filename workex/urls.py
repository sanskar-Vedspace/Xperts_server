from django.urls import path
from .views import WorkExperienceListCreateView

urlpatterns = [
    path('work-experiences/', WorkExperienceListCreateView.as_view(), name='work-experience-list-create'),
]

