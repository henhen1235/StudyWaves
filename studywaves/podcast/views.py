from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from googleapiclient.discovery import build
from google.oauth2 import Credentials

@login_required
def index(request):
    try:
        user_social = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        return redirect('social:begin', backend='google-oauth2')

    # get creds
    credentials = Credentials(
        token = user_social.extra_data['access_token'],
        refresh_token = user_social.extra_data.get('refresh_token'),
        token_uri = 'https://oauth2.googleapis.com/token',
        
        scopes = ['https://www.googleapis.com/auth/drive.readonly'],
    )

    service = build('drive', 'v3', credentials=credentials)
    results = service.files().list(pageSize=10, fields = "files(id, name)").execute()
    files = results.get('files', [])

    return render(request, 'podcast/index.html', {'files': files})