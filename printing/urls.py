from django.urls import path
from . import views

app_name = 'printer'
urlpatterns = [
    
     path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
     path('order/<int:order_id>/pdf/', views.generate_and_save_pdf, name='generate_pdf'),
    
   
]