from django.urls import path
from . import views



urlpatterns = [
    #path('', views.store, name='store'),
    path('show_category/', views.show_category, name='show_category'),

   
]
