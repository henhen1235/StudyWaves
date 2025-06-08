from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('audio-player/<int:podcast_id>/', views.audio_player, name='audio_player'),
    path('api/ask-question/', views.ask_question, name='ask_question'),
    path('create-podcast/', views.create_podcast, name='create_podcast'),
]