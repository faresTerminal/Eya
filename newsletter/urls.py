from django.urls import path
from . import views


app_name = 'newsletter'
urlpatterns = [
    #path('', views.store, name='store'),
    #path('subscribe/', views.subscribe_to_newsletter, name='subscribe_to_newsletter'),
    #this url to send update newsletters
    path('send-daily-slide/', views.send_daily_slide_email, name='send_daily_slide_email'),
    path('thank-you/', views.send_newsletter, name='thank_you'),
    #path('already_subscribed/', views.already_subscribed, name='already_subscribed'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),


   
   
]

