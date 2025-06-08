# flashcards/views.py
from podcast.models import Podcast 
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator
import json
import os
from google import genai
from google.genai import types
from .models import FlashcardSet, Flashcard, StudySession
from .forms import FlashcardSetForm, NotesForm
from dotenv import load_dotenv
import os

load_dotenv()


@login_required
def generate_flashcards_from_podcast(request, podcast_id):
    """Generate flashcards from podcast script"""
    podcast = get_object_or_404(Podcast, id=podcast_id)
    
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            notes = podcast.script  # Use the podcast script as notes
            
            try:
                # Generate flashcards using Gemini
                flashcards_text = generate_flashcards_with_gemini(notes)
                
                # Parse and save flashcards
                flashcard_set = FlashcardSet.objects.create(
                    title=title,
                    description=f"Generated from podcast: {podcast.title}",
                    created_by=request.user
                )
                
                flashcards = parse_flashcards_text(flashcards_text)
                
                for i, (term, definition) in enumerate(flashcards):
                    Flashcard.objects.create(
                        flashcard_set=flashcard_set,
                        term=term,
                        definition=definition,
                        order=i
                    )
                
                messages.success(request, f'Successfully generated {len(flashcards)} flashcards from podcast!')
                return redirect('flashcards:set_detail', set_id=flashcard_set.id)
                
            except Exception as e:
                messages.error(request, f'Error generating flashcards: {str(e)}')
    else:
        # Pre-populate the form with podcast title
        initial = {
            'title': f"Flashcards from {podcast.title}",
        }
        form = NotesForm(initial=initial)
    
    context = {
        'form': form,
        'podcast': podcast,
    }
    return render(request, 'flashcards/generate_from_podcast.html', context)


def flashcard_sets_list(request):
    """Display all flashcard sets"""
    sets = FlashcardSet.objects.all()
    if request.user.is_authenticated:
        user_sets = sets.filter(created_by=request.user)
        other_sets = sets.exclude(created_by=request.user)
    else:
        user_sets = []
        other_sets = sets
    
    context = {
        'user_sets': user_sets,
        'other_sets': other_sets,
    }
    return render(request, 'flashcards/sets_list.html', context)

def flashcard_set_detail(request, set_id):
    """Display a specific flashcard set"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = flashcard_set.flashcards.all()
    
    context = {
        'flashcard_set': flashcard_set,
        'flashcards': flashcards,
        'total_cards': flashcards.count(),
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
def generate_flashcards_from_notes(request):
    """Generate flashcards from notes using Gemini AI"""
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = form.cleaned_data['notes']
            title = form.cleaned_data['title']
            
            try:
                # Generate flashcards using Gemini
                flashcards_text = generate_flashcards_with_gemini(notes)
                
                # Parse and save flashcards
                flashcard_set = FlashcardSet.objects.create(
                    title=title,
                    description=f"Generated from notes",
                    created_by=request.user
                )
                
                flashcards = parse_flashcards_text(flashcards_text)
                
                for i, (term, definition) in enumerate(flashcards):
                    Flashcard.objects.create(
                        flashcard_set=flashcard_set,
                        term=term,
                        definition=definition,
                        order=i
                    )
                
                messages.success(request, f'Successfully generated {len(flashcards)} flashcards!')
                return redirect('flashcards:set_detail', set_id=flashcard_set.id)
                
            except Exception as e:
                messages.error(request, f'Error generating flashcards: {str(e)}')
    else:
        form = NotesForm()
    
    return render(request, 'flashcards/generate_from_notes.html', {'form': form})

def generate_flashcards_with_gemini(notes):
    """Generate flashcards using Gemini AI"""
    client = genai.Client(
        api_key=os.environ.get("GOOGLE_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=notes),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are a helpful study assistant.

You will be given user notes. Your task is to turn them into flashcards for studying.

At the very top, list the total number of flashcards in the format:
(Number of flashcards)

Then format each flashcard like this, with exactly one blank line between flashcards:

Flashcard [number]:
Term: [Insert term here]  
Definition: [Insert clear, concise definition here]

Important guidelines:

Do not add extra commentary, summaries, or explanations outside the flashcards.

Only include terms and definitions relevant to the provided notes.

Keep definitions short and easy to memorize.

Maintain consistent formatting throughout."""),
        ],
    )
    
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )
    
    return response.text

def parse_flashcards_text(text):
    """Parse the Gemini-generated flashcards text into term-definition pairs"""
    flashcards = []
    lines = text.strip().split('\n')
    
    current_term = None
    current_definition = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Term:'):
            current_term = line.replace('Term:', '').strip()
        elif line.startswith('Definition:'):
            current_definition = line.replace('Definition:', '').strip()
            if current_term and current_definition:
                flashcards.append((current_term, current_definition))
                current_term = None
                current_definition = None
    
    return flashcards

@csrf_exempt
def api_flashcards(request, set_id):
    """API endpoint to get flashcards for a set"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id)
    flashcards = list(flashcard_set.flashcards.all().values('id', 'term', 'definition'))
    
    return JsonResponse({'flashcards': flashcards})

@login_required
def delete_flashcard_set(request, set_id):
    """Delete a flashcard set"""
    flashcard_set = get_object_or_404(FlashcardSet, id=set_id, created_by=request.user)
    
    if request.method == 'POST':
        flashcard_set.delete()
        messages.success(request, 'Flashcard set deleted successfully!')
        return redirect('flashcards:sets_list')
    
    return render(request, 'flashcards/confirm_delete.html', {'flashcard_set': flashcard_set})