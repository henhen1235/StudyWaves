from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from podcast.models import Podcast
from .models import FlashcardSet, Flashcard
from .forms import FlashcardSetForm
from dotenv import load_dotenv
import json
import os
from google import genai
from google.genai import types

load_dotenv()

# Home and Podcast Views
def home(request):
    """Homepage with list of podcasts and flashcard sets"""
    podcasts = Podcast.objects.all().order_by('-created_at')
    flashcard_sets = FlashcardSet.objects.all().order_by('-created_at')
    
    context = {
        'podcasts': podcasts,
        'flashcard_sets': flashcard_sets,
    }
    return render(request, 'flashcards/home.html', context)

def podcast_player_redirect(request, podcast_id):
    """Redirect to the actual podcast player"""
    return redirect(f'/audio-player/{podcast_id}')

# Flashcard Views
def flashcard_set_detail(request, set_id):
    """Display a specific flashcard set"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = flashcard_set.flashcards.all()
    
    context = {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
    }
    return render(request, 'flashcards/set_detail.html', context)

def study_flashcards(request, set_id):
    """Study interface for flashcards"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = list(flashcard_set.flashcards.all().values('id', 'term', 'definition'))
    
    context = {
        'flashcard_set': flashcard_set,
        'flashcards_json': json.dumps(flashcards),
    }
    return render(request, 'flashcards/study.html', context)

@login_required
def create_flashcard_set(request):
    """Create a new flashcard set manually"""
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            flashcard_set = form.save(commit=False)
            flashcard_set.created_by = request.user
            flashcard_set.save()
            messages.success(request, 'Flashcard set created successfully!')
            return redirect('flashcards:set_detail', set_id=flashcard_set.id)
    else:
        form = FlashcardSetForm()
    
    return render(request, 'flashcards/create_set.html', {'form': form})

@login_required
def generate_flashcards_from_podcast(request, podcast_id):
    """Generate flashcards from podcast script"""
    podcast = get_object_or_404(Podcast, id=podcast_id)
    
    if request.method == 'POST':
        title = request.POST.get('title', f"Flashcards from {podcast.title}")
        
        try:
            # Check if flashcards already exist for this podcast
            existing_set = FlashcardSet.objects.filter(podcast=podcast).first()
            if existing_set:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Flashcards already exist for this podcast',
                        'set_id': existing_set.id
                    })
                messages.warning(request, 'Flashcards already exist for this podcast')
                return redirect('flashcards:set_detail', set_id=existing_set.id)
            
            # Generate flashcards using Gemini
            flashcards_text = generate_flashcards_with_gemini(podcast.script)
            
            # Parse and save flashcards
            flashcard_set = FlashcardSet.objects.create(
                title=title,
                description=f"Generated from podcast: {podcast.title}",
                created_by=request.user,
                podcast=podcast
            )
            
            flashcards = parse_flashcards_text(flashcards_text)
            
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
            
            messages.success(request, f'Successfully generated {len(flashcards)} flashcards!')
            return redirect('flashcards:set_detail', set_id=flashcard_set.id)
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': f'Error generating flashcards: {str(e)}'
                }, status=500)
            
            messages.error(request, f'Error generating flashcards: {str(e)}')
            return redirect('flashcards:podcast_redirect', podcast_id=podcast_id)
    
    return redirect('flashcards:podcast_redirect', podcast_id=podcast_id)

# Helper Functions
def generate_flashcards_with_gemini(notes):
    """Generate flashcards using Gemini AI"""
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    model = "gemini-2.5-flash-preview-05-20"
    
    response = client.models.generate_content(
        model=model,
        contents=[types.Content(parts=[types.Part.from_text(text=notes)])],
        config=types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(text="Convert notes into flashcards with Term: and Definition: format")
            ]
        )
    )
    return response.text

def parse_flashcards_text(text):
    """Parse generated flashcards into term-definition pairs"""
    flashcards = []
    current_term = None
    
    for line in text.split('\n'):
        line = line.strip()
        if line.startswith('Term:'):
            current_term = line[5:].strip()
        elif line.startswith('Definition:') and current_term:
            definition = line[10:].strip()
            flashcards.append((current_term, definition))
            current_term = None
    
    return flashcards

@csrf_exempt
def api_flashcards(request, set_id):
    """API endpoint for flashcards"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = list(flashcard_set.flashcards.all().values('id', 'term', 'definition'))
    return JsonResponse({'flashcards': flashcards})

@login_required
def delete_flashcard_set(request, set_id):
    """Delete a flashcard set"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id, created_by=request.user)
    if request.method == 'POST':
        flashcard_set.delete()
        messages.success(request, 'Flashcard set deleted!')
        return redirect('flashcards:home')
    return render(request, 'flashcards/confirm_delete.html', {'flashcard_set': flashcard_set})