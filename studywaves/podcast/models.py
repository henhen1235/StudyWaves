from django.db import models

# Functions to replace lambdas for upload paths
def podcast_script_upload_path(instance, filename):
    return f'static/AI/podcasts/{instance.id}/{filename}'

def audio_segment_upload_path(instance, filename):
    return f'static/AI/podcasts/{instance.podcast.id}/{filename}'

# Create your models here.
class Podcast(models.Model):
    title = models.CharField(max_length=200)
    script = models.TextField()  # Changed from FileField to TextField
    created_at = models.DateTimeField(auto_now_add=True)


    
class Segment(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='audio_segments', on_delete=models.CASCADE)
    path = models.TextField(max_length=200)