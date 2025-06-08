# flashcards/urls.py
from django.urls import path
from . import views

app_name = 'flashcards'

urlpatterns = [
    # Home and Podcast Views
    path('', views.home, name='home'),
    path('podcast/<int:podcast_id>/', views.podcast_player_redirect, name='podcast_redirect'),
    path('podcast/<int:podcast_id>/generate/', views.generate_flashcards_from_podcast, name='generate_from_podcast'),
    
    # Flashcard Views
    path('sets/', views.home, name='sets_list'),  # Add this line - reusing home view
    path('sets/<int:set_id>/', views.flashcard_set_detail, name='set_detail'),
    path('sets/<int:set_id>/study/', views.study_flashcards, name='study'),
    path('sets/create/', views.create_flashcard_set, name='create_set'),
    path('sets/<int:set_id>/delete/', views.delete_flashcard_set, name='delete_set'),
    
    # API Endpoint
    path('api/sets/<int:set_id>/flashcards/', views.api_flashcards, name='api_flashcards'),
]

