from django.urls import path
from .views import TimeBlockListView, TimeBlockDetailView

urlpatterns = [
    path('time-blocks/', TimeBlockListView.as_view(), name='time-block-list'),
    path('time-blocks/<int:pk>/', TimeBlockDetailView.as_view(), name='time-block-detail'),
]
