# flashcards/urls.py
from django.urls import path
from . import views

app_name = 'flashcards'

urlpatterns = [
    # Main flashcard views
    path('', views.flashcard_sets_list, name='sets_list'),
    path('set/<int:set_id>/', views.flashcard_set_detail, name='set_detail'),
    path('study/<int:set_id>/', views.study_flashcards, name='study'),
    
    # Create and manage sets
    path('create/', views.create_flashcard_set, name='create_set'),
    path('generate/', views.generate_flashcards_from_notes, name='generate_from_notes'),
    path('delete/<int:set_id>/', views.delete_flashcard_set, name='delete_set'),
    path('generate/podcast/<int:podcast_id>/', views.generate_flashcards_from_podcast, name='generate_from_podcast'),
    
    # API endpoints
    path('api/set/<int:set_id>/flashcards/', views.api_flashcards, name='api_flashcards'),
]