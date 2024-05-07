from django.test import TestCase, Client
from django.contrib.auth import get_user_model
import structlog
import os
from .models import TranscribePost
from .models import BlogPost
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate, login, logout

logger = structlog.get_logger()
user = 'testuser'
password = 'password'
youtube_title='Test'
youtube_link='TestYoutubeLink'
generated_content='TestContent'

# Create your tests here.

# class to test database
class ModelTest(TestCase):
       
    # test Transcriber table
    def test_models_transcribe(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)
        
        # logger.debug("test_models_transcribe():self.user.username=" + self.user.username)

        # Count the records
        transcribeCount = TranscribePost.objects.count()

        # test the record number
        self.assertEqual(0, transcribeCount)
            
        # create new record in the trancriber table
        new_transcribe_article = TranscribePost.objects.create(
            user=self.user,
            youtube_title=youtube_title,
            youtube_link=youtube_link,
            generated_content=generated_content,
        )
        new_transcribe_article.save()

        # Count the records
        transcribeCount = TranscribePost.objects.count()
        
        # logger.debug("test_models_transcribe():transcribeCount=" + str(transcribeCount))
        
        # test the record number
        self.assertEqual(1, transcribeCount)
        
        # logger.debug("test_models_transcribe():new_transcribe_article.youtube_title=" + new_transcribe_article.__str__())
        
        # get title
        self.assertEqual(new_transcribe_article.__str__(), new_transcribe_article.youtube_title)
        
    # test BlogPost table
    def test_models_blog_post(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)

        # logger.debug("test_models_blogpost():self.user.username=" + self.user.username)
 
        # Count the records
        blog_postCount = BlogPost.objects.count()

        # test the record number
        self.assertEqual(0, blog_postCount)
                        
        # create new record in the Blog Post table
        new_blog_post_article = BlogPost.objects.create(
            user=self.user,
            youtube_title=youtube_title,
            youtube_link=youtube_link,
            generated_content=generated_content,
        )
        new_blog_post_article.save()

        # Count the records
        blog_postCount = BlogPost.objects.count()
        
        # logger.debug("test_models_blogpost():blog_postCount=" + str(blog_postCount))
        
        # test the record number
        self.assertEqual(1, blog_postCount)
        
        # logger.debug("test_models_blogpost():new_blogpost_article.__str__()=" + new_blogpost_article.__str__())
        
        # get title
        self.assertEqual(new_blog_post_article.__str__(), new_blog_post_article.youtube_title)

# class to test html pages
class HTMLPageTest(TestCase):
    # test home page with logon (blog AI)
    def test_homepage(self):
        # create user instance
        # user = User.objects.create(username='testuser')
        # user.set_password(password)
        # user.save()
        self.user = User.objects.create_user(username=user, password=password)
        
        client = Client()
        
        # login
        client.login(username=self.user.username, password=password)
        
        # call home page
        response = client.get('/', follow=True)
        
        # logger.debug("test_models_blogpost():response.status_code=" + str(response.status_code))
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'Welcome to IA Blog Generator')
  
     # test transcriber page with logon
    def test_transcriber_page(self):
        # create user instance
        # user = User.objects.create(username='testuser')
        # user.set_password(password)
        # user.save()
        self.user = User.objects.create_user(username=user, password=password)
        
        # create user instance
        client = Client()

        # login
        client.login(username=self.user.username, password=password)
        
        # call web page
        response = client.get('/transcriber', follow=True)
        
        # logger.debug("test_models_blogpost():response.status_code=" + str(response.status_code))
        
        # validate the status response
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'Welcome to Transcriber Generator')
        
     # test all blogs empty page
    def test_all_blog_post_page_empty(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)

        client = Client()
        
        # login
        client.login(username=self.user.username, password=password)

        # call web page
        response = client.get('/all-blogs', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'No Blog Post Yet')
        
     # test all blogs with data
    def test_all_blog_post_page_with_data(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)
        
        # create new record
        new_blog_post_article = BlogPost.objects.create(
            user=self.user,
            youtube_title=youtube_title,
            youtube_link=youtube_link,
            generated_content=generated_content,
        )
        new_blog_post_article.save()

        # Count the records
        blog_postCount = BlogPost.objects.count()

        # test the record number
        self.assertEqual(1, blog_postCount)
        
        client = Client()
        
        # login
        client.login(username=self.user.username, password=password)

        # call wen page
        response = client.get('/all-blogs', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, generated_content) 
        
    def test_all_transcribe_post_page_empty(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)

        client = Client()
        
        # login
        client.login(username=self.user.username, password=password)

        # call web page
        response = client.get('/all-transcribe', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'No Transcribe Post Yet') 
        
    def test_all_transcribe_post_page_with_data(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)
        
        # create new record
        new_transcribe_article = TranscribePost.objects.create(
            user=self.user,
            youtube_title=youtube_title,
            youtube_link=youtube_link,
            generated_content=generated_content,
        )
        new_transcribe_article.save()

        # Count the records
        transcribeCount = TranscribePost.objects.count()

        # test the record number
        self.assertEqual(1, transcribeCount)
                
        client = Client()
        
        # login
        client.login(username=self.user.username, password=password)

        # call web page
        response = client.get('/all-transcribe', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, generated_content)
