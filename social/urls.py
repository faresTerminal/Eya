from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
     path('social/', views.social, name='social'),
     
]