from django.db import models
from django.contrib.auth import get_user_model
from google.oauth2.credentials import Credentials

User = get_user_model()

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credentials = models.JSONField()

    def save_credentials(self, credentials):
        self.credentials = credentials_to_dict(credentials)
        self.save()

    def get_credentials(self):
        return Credentials(**self.credentials)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
    }
