from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect
from django.conf import settings
from .models import GoogleCredentials,credentials_to_dict
from django.contrib.auth.decorators import login_required

@login_required
def google_auth(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    request.session['state'] = state
    return redirect(authorization_url)

@login_required
def oauth2callback(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_CLIENT_SECRETS,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=request.session['state'],
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
    )
    
    flow.fetch_token(authorization_response=request.get_full_path())
    credentials = flow.credentials

    # Save credentials in the GoogleCredentials model
    GoogleCredentials.objects.create(user=request.user, credentials=credentials_to_dict(credentials))
    
    return redirect('some-success-url')  # Redirect after successful connection
