from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.http import JsonResponse, HttpResponseForbidden
from googleapiclient.errors import HttpError
import PyPDF2
import docx
import io
import markdown
import html
import base64
from django.conf import settings

@login_required
def index(request):
    try:
        user_social = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        return redirect('social:begin', backend='google-oauth2')

    # Check if refresh_token is available
    refresh_token = user_social.extra_data.get('refresh_token')
    if not refresh_token:
        # Force re-authentication to get refresh token
        # This will redirect the user to the Google consent screen again
        return redirect('social:begin', backend='google-oauth2')

    credentials = Credentials(
        token=user_social.extra_data['access_token'],
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, # Use key from Django settings
        client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, # Use secret from Django settings
        scopes=['https://www.googleapis.com/auth/drive.readonly'],
    )

    service = build('drive', 'v3', credentials=credentials)
    
    all_files = []
    page_token = None
    query = "mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType='application/msword' or mimeType='application/pdf'"
    while True:
        results = service.files().list(
            q=query,
            pageSize=100,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token
        ).execute()
        all_files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    # sort files
    pdf_files = []
    word_files = []
    gdoc_files = []

    for file in all_files:
        mime_type = file.get('mimeType', '')
        if mime_type == 'application/pdf':
            pdf_files.append(file)
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mime_type == 'application/msword':
            word_files.append(file)
        elif mime_type == 'application/vnd.google-apps.document':
            gdoc_files.append(file)
        # else:
            # Optionally handle or log files that don't match expected types

    sorted_files = pdf_files + word_files + gdoc_files

    return render(request, 'podcast/index.html', {'files': sorted_files})

@login_required
def get_file_content(request, file_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("User not authenticated")

    try:
        user_social = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        return JsonResponse({'error': 'Google account not linked or session expired.'}, status=403)

    refresh_token = user_social.extra_data.get('refresh_token')
    if not refresh_token:
        # It's an API endpoint, so redirecting might not be ideal.
        # Return an error instructing the client to re-authenticate.
        return JsonResponse({'error': 'Missing refresh token. Please re-authenticate.', 'reauth_required': True}, status=401)

    credentials = Credentials(
        token=user_social.extra_data['access_token'],
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY, # Use key from Django settings
        client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET, # Use secret from Django settings
        scopes=['https://www.googleapis.com/auth/drive.readonly'],
    )

    service = build('drive', 'v3', credentials=credentials)

    try:
        file_metadata = service.files().get(fileId=file_id, fields='mimeType, name').execute()
        mime_type = file_metadata.get('mimeType', '')
        file_name = file_metadata.get('name', 'File')

        if mime_type == 'application/vnd.google-apps.document':            # export as rich text
            request_export = service.files().export_media(fileId=file_id, mimeType='text/html')
            file_content_bytes = request_export.execute()
            content = file_content_bytes.decode('utf-8', errors='replace')
            return JsonResponse({'name': file_name, 'content': content, 'mimeType': mime_type, 'contentType': 'html'})
        
        elif mime_type == 'application/pdf':
            file_content_bytes = service.files().get_media(fileId=file_id).execute()
            try:
                # encode pdf as base64 for pdf.js
                pdf_base64 = base64.b64encode(file_content_bytes).decode('utf-8')
                return JsonResponse({'name': file_name, 'content': pdf_base64, 'mimeType': mime_type, 'contentType': 'pdf'})
            except Exception as e:
                return JsonResponse({'name': file_name, 'content': f'Error reading PDF: {str(e)}', 'mimeType': mime_type, 'contentType': 'text'})

        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            file_content_bytes = service.files().get_media(fileId=file_id).execute()
            try:
                doc_file = io.BytesIO(file_content_bytes)
                doc = docx.Document(doc_file)
                
                html_content = ""
                for paragraph in doc.paragraphs:
                    para_html = ""
                    for run in paragraph.runs:
                        text = html.escape(run.text)
                        if run.bold:
                            text = f"<strong>{text}</strong>"
                        if run.italic:
                            text = f"<em>{text}</em>"
                        if run.underline:
                            text = f"<u>{text}</u>"
                        para_html += text
                    
                    if para_html.strip():
                        html_content += f"<p>{para_html}</p>\n"
                    else:
                        html_content += "<br>\n"
                
                if html_content.strip():
                    return JsonResponse({'name': file_name, 'content': html_content, 'mimeType': mime_type, 'contentType': 'html'})
                else:
                    return JsonResponse({'name': file_name, 'content': 'No readable content found in this document.', 'mimeType': mime_type, 'contentType': 'text'})
            except Exception as e:
                return JsonResponse({'name': file_name, 'content': f'Error reading Word document: {str(e)}', 'mimeType': mime_type, 'contentType': 'text'})

        elif mime_type == 'application/msword':
            # .doc files are more complex to parse, fallback to simple message
            return JsonResponse({'name': file_name, 'content': 'Legacy .doc files are not supported. Please convert to .docx format.', 'mimeType': mime_type, 'contentType': 'text'})
        
        else:
            return JsonResponse({'name': file_name, 'content': f"File type ({mime_type}) is not supported for direct preview.", 'mimeType': mime_type, 'contentType': 'text'})

    except HttpError as error:
        return JsonResponse({'error': f'An API error occurred: {error.resp.status} - {error._get_reason()}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)