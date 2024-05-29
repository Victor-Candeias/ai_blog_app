from django.test import TestCase, Client
import structlog
from blog_generator import views
from django.contrib.auth.models import User
from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse

logger = structlog.get_logger()
user: str = 'dummyuser'
password: str = 'dummypassword'
youtube_title: str ='Test'
youtube_link: str ='https://youtu.be/7IocRCDWB5k?list=RD7IocRCDWB5k'
generated_content: str ='Generated Content'
email: str = 'teste@ctt.ctt'

# Create your tests here.

# *******************************************************************
# Test tables
class ModelTest(TestCase):
       
    # *******************************************************************
    # Test add records to Transcriber table
    def test_models_transcribe(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)
        
        # create new record in the trancriber table
        save_result = views.save_transcribe_data(self.user, youtube_title, youtube_link, generated_content)
        
        # logger.debug("test_models_transcribe():save_result=" + str(save_result))
        
        # test if record was added
        self.assertEqual(True, save_result)
        
    # *******************************************************************
    # Test add records to Blog table
    def test_models_blog_post(self):
        # create user instance
        self.user = User.objects.create_user(username=user, password=password)

        # create new record in the Blog Post table
        save_result = views.save_blog_data(self.user, youtube_title, youtube_link, generated_content)
        
        # logger.debug("test_models_blogpost():save_result=" + str(save_result))
        
        # test if record was added
        self.assertEqual(True, save_result)

# *******************************************************************
# Test HTML pages
class HTMLPageTest(TestCase):
    # *******************************************************************
    # Test OpenAI page with user logon
    def test_homepage(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)

        # Access the HTML page that requires login
        response = self.client.get('/', follow=True)

        # Assert that the response status is as expected (e.g., 200 for success, or 302 for redirect)
        self.assertEqual(response.status_code, 200)

        # Optionally, you can check for the presence of elements or content on the page
        self.assertContains(response, "Welcome to IA Blog Generator")
  
    # *******************************************************************
    # Test transcriber page with user logon
    def test_transcriber_page(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)

        # Access the HTML page that requires login
        response = self.client.get('/transcriber', follow=True)

        # Assert that the response status is as expected (e.g., 200 for success, or 302 for redirect)
        self.assertEqual(response.status_code, 200)

        # Optionally, you can check for the presence of elements or content on the page
        self.assertContains(response, "Welcome to Transcriber Generator")
        
    # *******************************************************************
    # Test OpenAi blog page without records 
    def test_all_blog_post_page_empty(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)

        # call web page
        response = self.client.get('/all-blogs', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'No Blog Post Yet')
        
    # *******************************************************************
    # Test OpenAi blog page with records  
    def test_all_blog_post_page_with_data(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)
        
        # create new record
        save_result = views.save_blog_data(self.user, youtube_title, youtube_link, generated_content)

        # test if record was added
        self.assertEqual(True, save_result)
        
        # call wen page
        response = self.client.get('/all-blogs', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, generated_content) 

    # *******************************************************************
    # Test transcribe blog page without records         
    def test_all_transcribe_page_empty(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)

        # call web page
        response = self.client.get('/all-transcribe', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, 'No Transcribe Post Yet') 
    
    # *******************************************************************
    # Test transcribe blog page with records   
    def test_all_transcribe_page_with_data(self):
        # create user instance
        self.client = Client()
        self.username = user
        self.password = password
        self.user = User.objects.create_user(username=self.username, email=email, password=self.password)

        # Simulate logging in the user
        self.client.login(username=self.username, password=self.password)
        
        # create new record
        save_result = views.save_transcribe_data(self.user, youtube_title, youtube_link, generated_content)
        
        # test if record was added
        self.assertEqual(True, save_result)
                
        # call web page
        response = self.client.get('/all-transcribe', follow=True)
        
        # validate response code
        self.assertEqual(response.status_code, 200)
        
        # validate if text exists in page
        self.assertContains(response, generated_content)
