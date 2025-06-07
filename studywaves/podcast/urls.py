from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('get-file-content/<str:file_id>/', views.get_file_content, name='get_file_content'),
    path('audio-player/', views.audio_player, name='audio_player'),
    path('api/ask-question/', views.ask_question, name='ask_question'),
]