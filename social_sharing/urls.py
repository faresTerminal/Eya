# urls.py
from django.urls import path
from . import views



app_name = 'social_sharing'
urlpatterns = [
    path('facebook/login/', views.facebook_login, name='facebook_login'),
    path('facebook/callback/', views.facebook_callback, name='facebook_callback'),
]
