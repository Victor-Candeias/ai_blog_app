from django.contrib import admin
from .models import BlogPost, TranscribePost

# Register your models here.
# register the DB to the site
# date bases
admin.site.register(BlogPost)
admin.site.register(TranscribePost)