from django.db import models

from django.db import models
from django.contrib.auth.models import User

class FlashcardSet(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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

class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_cards = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.flashcard_set.title}"
