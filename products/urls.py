from django.urls import path
from . import views



urlpatterns = [
    
    path('add-product/', views.add_product, name='add_product'),
    path('add-variants/<int:product_id>/', views.add_variants, name='add_variants'),
    path('add-gallery-images/<int:product_id>/', views.add_gallery_images, name='add_gallery_images'),
    path('list_clearance_products/', views.list_clearance_products, name='list_clearance_products'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('add_description/<int:product_id>/', views.add_description, name='add_description'),

    
    

   
   
]