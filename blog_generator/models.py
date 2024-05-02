from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# datebase model
# blog
class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_title = models.CharField(max_length=1000)
    youtube_link = models.URLField()
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # return the youtube title
    def __str__(self):
        return self.youtube_title
    
# transcribe
class TranscribePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_title = models.CharField(max_length=1000)
    youtube_link = models.URLField()
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    # return the youtube title
    def __str__(self):
        return self.youtube_title