from django.urls import path
from . import views


urlpatterns = [
     path('place_order/', views.place_order, name='place_order'),
    
     #path('order_complete/', views.order_complete, name='order_complete'),
     path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
    
]