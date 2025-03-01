from django.urls import path
from . import views



urlpatterns = [
    
    path('add-product/', views.add_product, name='add_product'),
    path('add-variants/<int:product_id>/', views.add_variants, name='add_variants'),
    path('add-gallery-images/<int:product_id>/', views.add_gallery_images, name='add_gallery_images'),
    path('list_clearance_products/', views.list_clearance_products, name='list_clearance_products'),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('add_description/<int:product_id>/', views.add_description, name='add_description'),


    path('products/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    
    path('products/<int:product_id>/<int:image_id>/remove/', views.remove_gallery_image, name='remove_gallery_image'),
    path('products/<int:product_id>/variants/<int:variant_id>/remove/', views.remove_variant, name='remove_variant'),
    path('', views.Management_Center, name='Management_Center'),
    path('management_center/', views.Management_Center, name='Management_Center'),
    
    
    

   
   
]