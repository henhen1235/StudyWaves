from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.http import JsonResponse, HttpResponseForbidden
from googleapiclient.errors import HttpError
import google.generativeai as genai  # Add this import for Gemini
import PyPDF2
import docx
import io
import markdown
import html
import base64
from django.conf import settings
import os
import json
import sys
import requests
from pydub import AudioSegment
from dotenv import load_dotenv
from murf import Murf  # Import the Murf library


load_dotenv()

@login_required
def index(request):
    try:
        user_social = request.user.social_auth.get(provider='google-oauth2')
    except UserSocialAuth.DoesNotExist:
        return redirect('social:begin', backend='google-oauth2')

    refresh_token = user_social.extra_data.get('refresh_token')
    if not refresh_token:
        return redirect('social:begin', backend='google-oauth2')

    credentials = Credentials(
        token=user_social.extra_data['access_token'],
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
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
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            orderBy="modifiedTime desc",
            pageToken=page_token
        ).execute()
        all_files.extend(results.get('files', []))
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return render(request, 'podcast/index.html', {'files': all_files})

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
        return JsonResponse({'error': 'Missing refresh token. Please re-authenticate.', 'reauth_required': True}, status=401)

    credentials = Credentials(
        token=user_social.extra_data['access_token'],
        refresh_token=refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        client_secret=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        scopes=['https://www.googleapis.com/auth/drive.readonly'],
    )

    service = build('drive', 'v3', credentials=credentials)

    try:
        file_metadata = service.files().get(fileId=file_id, fields='mimeType, name').execute()
        mime_type = file_metadata.get('mimeType', '')
        file_name = file_metadata.get('name', 'File')

        if mime_type == 'application/vnd.google-apps.document':
            request_export = service.files().export_media(fileId=file_id, mimeType='text/html')
            file_content_bytes = request_export.execute()
            content = file_content_bytes.decode('utf-8', errors='replace')
            return JsonResponse({'name': file_name, 'content': content, 'mimeType': mime_type, 'contentType': 'html'})
        
        elif mime_type == 'application/pdf':
            file_content_bytes = service.files().get_media(fileId=file_id).execute()
            try:
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
            return JsonResponse({'name': file_name, 'content': 'Legacy .doc files are not supported. Please convert to .docx format.', 'mimeType': mime_type, 'contentType': 'text'})
        
        else:
            return JsonResponse({'name': file_name, 'content': f"File type ({mime_type}) is not supported for direct preview.", 'mimeType': mime_type, 'contentType': 'text'})

    except HttpError as error:
        return JsonResponse({'error': f'An API error occurred: {error.resp.status} - {error._get_reason()}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def audio_player(request):
    directory = '/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/studywaves/static/AI/podcast'
    file_list = os.listdir(directory)

    valid_files = []

    for filename in file_list:
        if filename.startswith('male_') or filename.startswith('female_'):
            parts = filename.split('_')
            if len(parts) == 2 and parts[1].endswith('.mp3'):
                number_part = parts[1][:-4]  # remove '.mp3'
                if number_part.isdigit():
                    number = int(number_part)
                    valid_files.append((filename, number))

    # Sort the files by number
    for i in range(len(valid_files)):
        for j in range(i + 1, len(valid_files)):
            if valid_files[i][1] > valid_files[j][1]:
                valid_files[i], valid_files[j] = valid_files[j], valid_files[i]

    # Create the full static paths
    output = [filename for filename, _ in valid_files]  # Only the filename, not the path
    return render(request, 'podcast/audio_player.html', {'files': output})

# Add this function to your views.py file
# @csrf_exempt
def ask_question(request):
    """
    Custom implementation to handle user questions by generating audio responses
    that integrate seamlessly into the podcast.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        # Parse the request data
        data = json.loads(request.body)
        read_content = data.get('read', '')
        unread_content = data.get('unread', '')
        question = data.get('question', '')
        
        # Validate input
        if not question:
            return JsonResponse({'error': 'Question cannot be empty'}, status=400)
        
        # Load environment variables for API keys
        load_dotenv()
        
        # Prepare directories - use a relative path that matches your static file setup
        questions_dir = '/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/studywaves/static/AI/questions'
        if not os.path.exists(questions_dir):
            os.makedirs(questions_dir)
            
        # Clear existing files
        for file in os.listdir(questions_dir):
            file_path = os.path.join(questions_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        # Generate response script using Gemini
        response_script = generate_response_script(read_content, unread_content, question)
        if not response_script:
            return JsonResponse({'error': 'Failed to generate response script'}, status=500)
        
        # Convert script to audio files
        audio_files = generate_audio_files(response_script, questions_dir)
        if not audio_files:
            return JsonResponse({'error': 'Failed to generate audio files'}, status=500)
        
        # Return the relative paths to use with static files
        file_paths = [f'AI/questions/{filename}' for filename in audio_files]
        
        return JsonResponse({
            'success': True,
            'message': 'Response generated successfully',
            'audioFiles': file_paths,  # Using the correct relative paths
            'responseText': response_script
        })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

def generate_response_script(read, unread, question):
    """
    Generate a podcast script segment that answers the user's question
    while maintaining continuity with existing content.
    """
    try:
        # Initialize Gemini API
        genai.api_key = os.environ.get("GOOGLE_API_KEY") # Add this line
        genai.configure(api_key=genai.api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")
        
        # Create the prompt
        prompt = f"""
You are a helpful and creative podcast script editor.

You will be given:
- The podcast script so far: "{read[:2000]}..." (truncated for brevity)
- Upcoming script: "{unread[:2000]}..." (truncated for brevity)
- Listener question: "{question}"

Write a bridging script segment that:
1. Naturally flows from the previous content
2. Directly addresses the listener's question
3. Transitions smoothly to the upcoming content
4. Matches the tone and style of the podcast
5. Avoids repeating information from either the read or unread sections
6. Refer to the person asking the question ONLY as "Listener" in the script

Format your response as a podcast script with speaker labels:
**Speaker 1:** [Female host's dialogue]
**Speaker 2:** [Male host's dialogue]

Keep it concise and engaging, around 1-2 exchanges between speakers.
"""

        # Generate the response
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"Error generating script: {e}")
        return None

def generate_audio_files(script, output_dir):
    """
    Convert the script into audio files using text-to-speech.
    Creates separate files for each speaker turn.
    """
    try:
        # Split script into lines
        lines = script.strip().split('\n')
        audio_files = []
        file_index = 0
        
        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            if "**Speaker 1:**" in line:
                # Female voice
                text = line.replace("**Speaker 1:**", "").strip()
                filename = f"female_{file_index}.mp3"
                file_path = os.path.join(output_dir, filename)
                
                # Generate female voice audio
                generate_female_voice(text, file_path)
                audio_files.append(filename)
                file_index += 1
                
            elif "**Speaker 2:**" in line:
                # Male voice
                text = line.replace("**Speaker 2:**", "").strip()
                filename = f"male_{file_index}.mp3"
                file_path = os.path.join(output_dir, filename)
                
                # Generate male voice audio
                generate_male_voice(text, file_path)
                audio_files.append(filename)
                file_index += 1
        
        return audio_files
        
    except Exception as e:
        print(f"Error generating audio files: {e}")
        return []

def generate_female_voice(text, output_path):
    """
    Generate female voice audio using MurfAI Python library
    """
    try:
        # Initialize Murf client
        client = Murf(api_key=os.environ.get("MURF_API_KEY"))

        # Generate speech using Murf
        response = client.text_to_speech.generate(
            text=text,
            voice_id="en-US-natalie",  # Same as in your merge.py
            style="Conversational",
            multi_native_locale="en-US"
        )

        # Download and save the audio file
        try:
            audio_response = requests.get(response.audio_file)
            audio_response.raise_for_status()
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            print(f"Female voice audio file downloaded successfully as: {output_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading female voice audio file: {e}")
            raise
            
    except Exception as e:
        print(f"Error generating female voice with MurfAI: {e}")
        
        # Try using the function from merge.py as fallback
        try:
            ai_dir = '/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI'
            if ai_dir not in sys.path:
                sys.path.append(ai_dir)
                
            from merge import femalePodCaster
            femalePodCaster(text, output_path)
            return True
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            
            # Last resort: Create a silent file with some length
            with open(output_path, 'wb') as f:
                silence = AudioSegment.silent(duration=3000)
                silence.export(output_path, format="mp3")
            return False

def generate_male_voice(text, output_path):
    """
    Generate male voice audio using MurfAI Python library
    """
    try:
        # Initialize Murf client
        client = Murf(api_key=os.environ.get("MURF_API_KEY"))

        # Generate speech using Murf
        response = client.text_to_speech.generate(
            text=text,
            voice_id="en-US-charles",  # Same as in your merge.py
            style="Conversational",
            multi_native_locale="en-US"
        )

        # Download and save the audio file
        try:
            audio_response = requests.get(response.audio_file)
            audio_response.raise_for_status()
            
            # Save the audio file
            with open(output_path, 'wb') as f:
                f.write(audio_response.content)
            
            print(f"Male voice audio file downloaded successfully as: {output_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading male voice audio file: {e}")
            raise
            
    except Exception as e:
        print(f"Error generating male voice with MurfAI: {e}")
        
        # Try using the function from merge.py as fallback
        try:
            ai_dir = '/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI'
            if ai_dir not in sys.path:
                sys.path.append(ai_dir)
                
            from merge import malePodCaster
            malePodCaster(text, output_path)
            return True
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            
            # Last resort: Create a silent file with some length
            with open(output_path, 'wb') as f:
                silence = AudioSegment.silent(duration=3000)
                silence.export(output_path, format="mp3")
            return False
