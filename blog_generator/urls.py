from django.urls import path
from . import views # importa o ficheiro views.py

# list de todos os urls da app
urlpatterns = [
    path('', views.index, name='index'), # home page definida no ficheiro views.py a função index  vai estar definida no ficheiro views
    path('login', views.user_login, name='login'),
    path('signup', views.user_signup, name='signup'),
    path('logout', views.user_logout, name='logout'),
    path('generate-blog', views.generate_blog, name='generate-blog'),
    path('transcriber', views.transcriber, name='transcriber'),
    path('transcriber_blog', views.transcriber_blog, name='transcriber_blog'),
]