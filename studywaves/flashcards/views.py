from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from podcast.models import Podcast
from .models import FlashcardSet, Flashcard
from .forms import FlashcardSetForm
from dotenv import load_dotenv
import json
import os
from google import genai
from google.genai import types

load_dotenv()

def home(request):
    podcasts = Podcast.objects.all().order_by('-created_at')
    
    for podcast in podcasts:
        try:
            podcast.flashcard_set = FlashcardSet.objects.filter(podcast=podcast).first()
        except:
            podcast.flashcard_set = None
    
    flashcard_sets = FlashcardSet.objects.all().order_by('-created_at')
    
    context = {
        'podcasts': podcasts,
        'flashcard_sets': flashcard_sets,
    }
    return render(request, 'flashcards/home.html', context)

def podcast_player_redirect(request, podcast_id):
    return redirect(f'/audio-player/{podcast_id}')

def flashcard_set_detail(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = flashcard_set.flashcards.all()
    
    context = {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
        'total_cards': flashcards.count(),
    }
    return render(request, 'flashcards/set_detail.html', context)

def study_flashcards(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = list(flashcard_set.flashcards.all().values('id', 'term', 'definition'))
    
    context = {
        'flashcard_set': flashcard_set,
        'flashcards_json': json.dumps(flashcards),
    }
    return render(request, 'flashcards/study.html', context)

@login_required
def generate_flashcards_from_podcast(request, podcast_id):
    podcast = get_object_or_404(Podcast, id=podcast_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', f"Flashcards from {podcast.title}")
        
        try:
            existing_set = FlashcardSet.objects.filter(podcast=podcast).first()
            if existing_set:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Flashcards already exist for this podcast',
                        'set_id': existing_set.id
                    })
                return redirect('flashcards:set_detail', set_id=existing_set.id)
            
            if not hasattr(podcast, 'script') or not podcast.script:
                error_msg = 'No script found for this podcast. Cannot generate flashcards.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
                return redirect('flashcards:home')
            
            flashcards_text = generate_flashcards_with_gemini(podcast.script)
            
            if not flashcards_text:
                error_msg = 'Failed to generate flashcards content'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
                return redirect('flashcards:home')
            
            flashcard_set = FlashcardSet.objects.create(
                title=title,
                description=f"Generated from podcast: {podcast.title}",
                created_by=request.user,
                podcast=podcast
            )
            
            flashcards = parse_flashcards_text(flashcards_text)
            
            if not flashcards:
                flashcard_set.delete()
                error_msg = 'No valid flashcards could be generated from the podcast script'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    })
                return redirect('flashcards:home')
            
            for i, (term, definition) in enumerate(flashcards):
                Flashcard.objects.create(
                    flashcard_set=flashcard_set,
                    term=term,
                    definition=definition,
                    order=i
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'set_id': flashcard_set.id,
                    'message': f'Successfully generated {len(flashcards)} flashcards!'
                })
            
            return redirect('flashcards:set_detail', set_id=flashcard_set.id)
            
        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Error generating flashcards: {str(e)}'
                }, status=500)
            
            return redirect('flashcards:home')
    
    return redirect('flashcards:home')

def generate_flashcards_with_gemini(notes):
    try:
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        model = "gemini-2.0-flash-exp" 
        
        prompt = f"""
        Create flashcards from the following podcast transcript. 
        Extract key concepts, definitions, and important information.
        Format each flashcard exactly as:
        Term: [question or key concept]
        Definition: [answer or explanation]
        
        Make sure to:
        - Focus on important concepts and facts
        - Create clear, concise terms and definitions
        - Aim for 8-15 flashcards total
        - Use the exact format specified above
        
        Transcript:
        {notes}
        """
        
        response = client.models.generate_content(
            model=model,
            contents=[types.Content(parts=[types.Part.from_text(text=prompt)])],
            config=types.GenerateContentConfig(
                response_mime_type="text/plain",
                system_instruction=[
                    types.Part.from_text(text="You are a helpful assistant that creates educational flashcards from content.")
                ]
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        return None

def parse_flashcards_text(text):
    flashcards = []
    current_term = None
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('Term:'):
            current_term = line[5:].strip()
        elif line.startswith('Definition:') and current_term:
            definition = line[11:].strip()
            if current_term and definition:
                flashcards.append((current_term, definition))
            current_term = None
    
    return flashcards

@csrf_exempt
def api_flashcards(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = list(flashcard_set.flashcards.all().values('id', 'term', 'definition'))
    return JsonResponse({'flashcards': flashcards})

@login_required
def delete_flashcard_set(request, set_id):
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id, created_by=request.user)
    if request.method == 'POST':
        flashcard_set.delete()
        return redirect('flashcards:home')
    return render(request, 'flashcards/confirm_delete.html', {'flashcard_set': flashcard_set})