# flashcards/models.py
from django.db import models
from django.contrib.auth.models import User
from podcast.models import Podcast  # Add this import

class FlashcardSet(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    podcast = models.ForeignKey(Podcast, null=True, blank=True, on_delete=models.SET_NULL)  # Add this field
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Flashcard(models.Model):
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='flashcards')
    term = models.CharField(max_length=500)
    definition = models.TextField()
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.term} - {self.flashcard_set.title}"
    
    class Meta:
        ordering = ['order', 'id']