# expertise/urls.py
from django.urls import path
from .views import ExpertiseListView

urlpatterns = [
    path('', ExpertiseListView.as_view(), name='expertise-list'),
]
