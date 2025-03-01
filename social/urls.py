from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
     
     path('manage-pixels/', views.manage_pixels, name='manage_pixels'),
     path('delete-pixel/<int:pixel_id>/', views.delete_pixel, name='delete_pixel'),
     
]