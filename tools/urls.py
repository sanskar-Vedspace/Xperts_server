# tools/urls.py
from django.urls import path
from .views import ToolListView

urlpatterns = [
    path('', ToolListView.as_view(), name='tool-list'),
]
