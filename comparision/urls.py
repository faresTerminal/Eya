from django.urls import path
from . import views


urlpatterns = [
   
    
    
    path('comparison_result/', views.comparison_result, name='comparison_result'),
  
    path('product_search/', views.product_search, name='product_search'),

    ]