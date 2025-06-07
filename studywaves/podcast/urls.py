from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("file/<str:file_id>/", views.get_file_content, name='get_file_content'),
    path("audio-player/", views.audio_player, name='audio_player'),
]