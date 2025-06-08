# flashcards/forms.py
from django import forms
from .models import FlashcardSet

class FlashcardSetForm(forms.ModelForm):
    class Meta:
        model = FlashcardSet
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter flashcard set title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter description (optional)',
                'rows': 3
            }),
        }

class NotesForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter title for your flashcard set'
        }),
        help_text='Give your flashcard set a descriptive title'
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Paste your study notes here...',
            'rows': 15,
            'style': 'font-family: monospace;'
        }),
        help_text='Paste your study notes and AI will generate flashcards from them'
    )