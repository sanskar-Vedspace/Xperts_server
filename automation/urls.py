# automation/urls.py
from django.urls import path
from .views import google_auth, oauth2callback

urlpatterns = [
    path('google-auth/', google_auth, name='google_auth'),
    path('oauth2callback/', oauth2callback, name='oauth2callback'),
]
