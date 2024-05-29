from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json
from pytube import YouTube
import os
import assemblyai as aai
from openai import OpenAI
import structlog
import datetime
import sys
from .models import BlogPost, TranscribePost

# Start logger
logger = structlog.get_logger()

# Create your views here.

# ***************************************************************************
# Indicate that require logon to access to index
@login_required
# Index page function
def index(request):
    return render(request, 'index.html')

# ***************************************************************************
# Transcriber page function
@login_required
def transcriber(request):
    return render(request, 'transcriber.html')

# ***************************************************************************
# Doesn't need csrf
@csrf_exempt
# Transcriber page function - create the transcriber
def transcriber_blog(request):
    # logger.debug("transcriber():request.method=" + request.method)
    # logger.debug("transcriber():settings.MEDIA_ROOT=" + settings.MEDIA_ROOT)
    # logger.debug("transcriber():settings.MEDIA_LOG=" + settings.LOG)
    write_log('transcriber_blog()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
                    
    # if the method is POST
    if request.method == 'POST':
        yt_link = ''
        
        try:
            # json vem tipo lista
            data = json.loads(request.body)
            
            # extraimos da lista o id link que foi dado 
            yt_link = data['link']                   

        except (KeyError, json.JSONDecodeError):
            write_log('transcriber_blog()', '1.KeyError.LOG=' + sys.exc_info()[1])
            return JsonResponse({'Error': 'Invalid request sent'}, status=400)  
        
        # get yt title
        title = yt_title(yt_link)

        # logger.debug("transcriber_blog():title=" + title)
        write_log('transcriber_blog()', 'title=' + title)

        # get transcript
        transcription = get_transcript(yt_link)
        if not transcription:
            write_log('transcriber_blog()', 'transcription does not exist')
            return JsonResponse({'Error': 'Failed to get transcript'}, status=500)

        # save blog article to database
        save_transcribe_data(request.user, title, yt_link, transcription)
        
        # return blog article as response
        write_log('transcriber_blog()', 'transcription=' + transcription)
        
        return JsonResponse({'content': transcription}, status=200)
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=405)

def save_transcribe_data(user: str | None, title: str | None, yt_link: str | None, transcription: str | None): 
    # save blog article to database
    new_transcribe_article = TranscribePost.objects.create(
        user=user,
        youtube_title=title,
        youtube_link=yt_link,
        generated_content=transcription,
    )
    
    try:
        # validate data
        new_transcribe_article.full_clean()
    except ValidationError:
        # handle error
        write_log('save_transcribe_data()', 'ValidationError=' + ValidationError.message)
        
        return False
    else:
        # save data
        new_transcribe_article.save()
        
        return True
        
# ***************************************************************************
# Doesn't need csrf
@csrf_exempt
# Generate blog information from a input user text and using OpenAI
def generate_blog(request):
    
    # logger.debug("generate_blog():request.method=" + request.method)
    # logger.debug("generate_blog():settings.MEDIA_ROOT=" + settings.MEDIA_ROOT)
    # logger.debug("generate_blog():settings.MEDIA_LOG=" + settings.LOG)
    write_log('generate_blog()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
                    
    # if the method is POST
    if request.method == 'POST':
        yt_link = ''
        
        try:
            # json tipo lista
            data = json.loads(request.body)
            
            # extraimos da lista o id link que foi dado 
            yt_link = data['link']                   

        except (KeyError, json.JSONDecodeError):
            write_log('generate_blog()', '1.KeyError.LOG=' + sys.exc_info()[1])
            return JsonResponse({'Error': 'Invalid request sent'}, status=400)  

        # get yt title
        title = yt_title(yt_link)
        
        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(yt_link)
        if not blog_content:
            write_log('generate_blog()', 'blog_content does not exist')
            return JsonResponse({'Error': 'Failed to generate blog article'}, status=500)
        
        # save blog article to database
        save_blog_data(request.user, title, yt_link, blog_content)
        
        # return blog article as response
        write_log('generate_blog()', 'blog_content' + blog_content)
        return JsonResponse({'content': blog_content}, status=200)
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=405)

def save_blog_data(user: str | None, title: str | None, yt_link: str | None, transcription: str | None): 
    # save blog article to database
    new_blog_article = BlogPost.objects.create(
        user=user,
        youtube_title=title,
        youtube_link=yt_link,
        generated_content=transcription,
    )
    
    try:
        # validate data
        new_blog_article.full_clean()
    except ValidationError:
        # handle error
        write_log('save_blog_data()', 'ValidationError=' + ValidationError.messages)
        return False
    else:
        # save data
        new_blog_article.save()
        return True

def blog_data_get_last_item_id():
    return BlogPost.objects.latest('pk')

# ***************************************************************************
# Get youtube video title
def yt_title(link: str | None):
    yt = YouTube(link)
    title = yt.title
    return title

# ***************************************************************************
# Download youtube video to mp3 format
def download_audio(link: str | None):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    
    logger.debug("download_audio():out_file=" + out_file)
    write_log('download_audio()', 'out_file=' + out_file)    

    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    
    if os.path.exists(new_file):
        os.remove(new_file)
        
    logger.debug("download_audio():new_file=" + new_file)
    write_log('download_audio()', 'new_file=' + new_file)     
    
    os.rename(out_file, new_file)
    
    return new_file

# ***************************************************************************
# Transcribe the youtube mp3 file to text
def get_transcript(link: str | None):
    audio_file = download_audio(link)
    
    logger.debug("get_transcript():audio_file=" + audio_file)
    write_log('get_transcript()', 'audio_file=' + audio_file) 
    
    logger.debug("get_transcript():settings.ASSEMBLY_AI_KEY=" + settings.ASSEMBLY_AI_KEY)
    write_log('get_transcript()', 'settings.ASSEMBLY_AI_KEY=' + settings.ASSEMBLY_AI_KEY) 
    
    aai.settings.api_key = settings.ASSEMBLY_AI_KEY
    
    logger.debug("get_transcript():aai.settings.api_key=" + aai.settings.api_key)
    write_log('get_transcript()', 'aai.settings.api_key=' + aai.settings.api_key) 
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    if transcript.status == aai.TranscriptStatus.error:
        logger.debug("get_transcript():transcript.error=" + transcript.error)
        write_log('get_transcript()', 'transcript.error=' + transcript.error)
        
        return transcript.error
    else:
        logger.debug("get_transcript():transcript.text=" + transcript.text)
        write_log('get_transcript()', 'transcript.text=' + transcript.text)
        
        return transcript.text

# ***************************************************************************
# Generate blog text using OpenAI
def generate_blog_from_transcription(transcription: str | None):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    logger.debug("generate_blog_from_transcription():transcript.text=" + client.api_key)
    write_log('generate_blog_from_transcription()', 'transcript.text=' + client.api_key)
            
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    logger.debug("generate_blog_from_transcription():prompt=" + prompt)
    write_log('generate_blog_from_transcription()', 'prompt=' + prompt)
        
    # "text-davinci-003"
    response = client.completions.create(model="davinci-002", 
                                      prompt = prompt, 
                                      max_tokens = 100)
    
    generator_content = response.choices[0].text.strip()

    logger.debug("generate_blog_from_transcription():generator_content=" + generator_content)
    write_log('generate_blog_from_transcription()', 'generator_content=' + generator_content)
        
    return generator_content

# ***************************************************************************
# User login method
def user_login(request):
    # if the method is POST
    if request.method == 'POST':
        # get form information
        username = request.POST['username']
        password = request.POST['password']
        
        result = user_authenticate(request, username, password)
        
        if result == True:
            # redirect to home page
            return redirect('/')      
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message}) 
                  
        # user = authenticate(request, username=username, password=password)
        
        # if user is not None:
        #     login(request, user)
        #     # redirect to home page
        #     return redirect('/')
        
        # else:
        #     error_message = 'Invalid username or password'
        #     return render(request, 'login.html', {'error_message': error_message})   
        
    return render(request, 'login.html')

def user_authenticate(request, username: str | None, password: str | None):
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        
        return True
    
    else:
        return False    
    
# ***************************************************************************
# User signup method
def user_signup(request):
    # if the method is POST
    if request.method == 'POST':
        # get form information
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']
        
        # validate if the password if the same of the repeat password
        if password == repeatPassword:
            try:
                # get user info to save to the BD
                user = User.objects.create_user(username, email, password)
                user.save()
                
                # login the user
                login(request, user)
                
                # redirect to home page
                return redirect('/')
                
            except:
                error_message = 'Password do not match'
                return render(request, 'signup.html', {'error_message': error_message})
        else:
            # Wrong password return error to the frontend
            error_message = 'Error creating account'
            return render(request, 'signup.html', {'error_message': error_message})
    
    # normal return
    return render(request, 'signup.html')

# ***************************************************************************
# User logout method
def user_logout(request):
    logout(request)
    # redirect to home page
    return redirect('/')

# ***************************************************************************
# Show transcriber list
def transcriber_list(request):
    trancriber_articles = TranscribePost.objects.filter(user=request.user)
    
    return render(request,'all-transcribe.html', {'trancriber_articles': trancriber_articles})

# ***************************************************************************
# Show blog list
def all_blogs(request):
    blog_articles = BlogPost.objects.filter(user=request.user)
    
    return render(request,'all-blogs.html', {'blog_articles': blog_articles})

# ***************************************************************************
# Show blog list details
def blog_details(request, pk):
    blog_article_details = BlogPost.objects.get(id=pk)
    
    if request.user == blog_article_details.user:
        return render(request,'blog-details.html', {'blog_article_details': blog_article_details})
    else:
        return redirect('/')

# ***************************************************************************
# Show transcribe list details
def transcribe_details(request, pk):
    trancrive_article_details = TranscribePost.objects.get(id=pk)
    
    if request.user == trancrive_article_details.user:
        return render(request,'transcribe-details.html', {'trancrive_article_details': trancrive_article_details})
    else:
        return redirect('/')

# ***************************************************************************
# Log to file method
def write_log(method: str | None, message: str | None):
    now=datetime.datetime.now()
    
    message = method + ';' + message
    
    with open(settings.LOG + "/" + now.strftime('%Y%m%d') + '_log.txt', 'a') as f:
        f.write("{}\n".format(now.isoformat() + ';' + message))  # python will convert \n to os.linesep