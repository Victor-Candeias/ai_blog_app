from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
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
def transcriber(request):
    return render(request, 'transcriber.html')

# ***************************************************************************
# Doesn't need csrf
@csrf_exempt
# Transcriber page function - create the transcriber
def transcriber_blog(request):
    logger.debug("transcriver():request.method=" + request.method)
    logger.debug("transcriver():settings.MEDIA_ROOT=" + settings.MEDIA_ROOT)
    logger.debug("transcriver():settings.MEDIA_LOG=" + settings.LOG)
    write_log('transcriver()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
    write_log('transcriver()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
    write_log('transcriver()', 'settings.LOG=' + settings.LOG)
                    
    # if the method is POST
    if request.method == 'POST':
        yt_link = ''
        
        try:
            # json vem tipo lista
            data = json.loads(request.body)
            
            # extraimos da lista o id link que foi dado 
            yt_link = data['link']                   

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'Error': 'Invalid request sent'}, status=400)  
        
        # get yt title
        title = yt_title(yt_link)

        logger.debug("generate_blog():title=" + title)
        write_log('generate_blog()', 'title=' + title)

        # get transcript
        transcription = get_transcript(yt_link)
        if not transcription:
            return JsonResponse({'Error': 'Failed to get transcript'}, status=500)

        return JsonResponse({'content': transcription}, status=200)
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=405)

# ***************************************************************************
# Doesn't need csrf
@csrf_exempt
# Generate blog information from a input user text and using OpenAI
def generate_blog(request):
    
    logger.debug("generate_blog():request.method=" + request.method)
    logger.debug("generate_blog():settings.MEDIA_ROOT=" + settings.MEDIA_ROOT)
    logger.debug("generate_blog():settings.MEDIA_LOG=" + settings.LOG)
    write_log('generate_blog()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
    write_log('generate_blog()', 'settings.MEDIA_ROOT=' + settings.MEDIA_ROOT)
    write_log('generate_blog()', 'settings.LOG=' + settings.LOG)
                    
    # if the method is POST
    if request.method == 'POST':
        yt_link = ''
        
        try:
            # json vem tipo lista
            data = json.loads(request.body)
            
            # extraimos da lista o id link que foi dado 
            yt_link = data['link']                   

        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'Error': 'Invalid request sent'}, status=400)  
        
        # get yt title
        # title = yt_title(yt_link)

        # logger.debug("generate_blog():title=" + title)
        # write_log('generate_blog()', 'title=' + title)

        # get transcript
        # transcription = get_transcript(yt_link)
        # if not transcription:
        #     return JsonResponse({'Error': 'Failed to get transcript'}, status=500)

        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(yt_link)
        if not blog_content:
            return JsonResponse({'Error': 'Failed to generate blog article'}, status=500)
        
        # save blog article to database

        # return blog article as response
        # return JsonResponse({'content': blog_content})
        return JsonResponse({'content': blog_content}, status=200)
    else:
        return JsonResponse({'Error': 'Invalid request method'}, status=405)

# ***************************************************************************
# Get youtube video title
def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

# ***************************************************************************
# Download youtube video to mp3 format
def download_audio(link):
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
def get_transcript(link):
    audio_file = download_audio(link)
    
    logger.debug("get_transcript():audio_file=" + audio_file)
    write_log('get_transcript()', 'audio_file=' + audio_file) 
    
    aai.settings.api_key = "053e732c73ef4ff395ad46b360aaaa50"
    
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
def generate_blog_from_transcription(transcription):
    OPENAI_API_KEY = "sk-proj-DAkkm3gYflEIi2D1rt7mT3BlbkFJvLJRSpbPiTUlYAWLRoo6"
    
    client = OpenAI(api_key=OPENAI_API_KEY)

    logger.debug("generate_blog_from_transcription():transcript.text=" + client.api_key)
    write_log('generate_blog_from_transcription()', 'transcript.text=' + client.api_key)
            
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    logger.debug("generate_blog_from_transcription():prompt=" + prompt)
    write_log('generate_blog_from_transcription()', 'prompt=' + prompt)
        
    # "text-davinci-003"
    response = client.completions.create(model="gpt-3.5-turbo-instruct", 
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
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # redirect to home page
            return redirect('/')
        
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})   
        
    return render(request, 'login.html')

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
        
        # validate if the password if the same of the repete password
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
# Log to file method
def write_log(method, message):
    now=datetime.datetime.now()
    
    message = method + ';' + message
    
    with open(settings.LOG + "/" + now.strftime('%Y%m%d') + '_log.txt', 'a') as f:
        f.write("{}\n".format(now.isoformat() + ';' + message))  # python will convert \n to os.linesep