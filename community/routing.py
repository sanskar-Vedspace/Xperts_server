# your_app_name/routing.py

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/posts/', consumers.PostConsumer.as_asgi()),  # Define your WebSocket endpoint here
]
