from django.db import models

def podcast_script_upload_path(instance, filename):
    return f'static/AI/podcasts/{instance.id}/{filename}'

def audio_segment_upload_path(instance, filename):
    return f'static/AI/podcasts/{instance.podcast.id}/{filename}'

class Podcast(models.Model):
    title = models.CharField(max_length=200)
    script = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    
class Segment(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='audio_segments', on_delete=models.CASCADE)
    path = models.TextField(max_length=200)