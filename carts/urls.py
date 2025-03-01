from django.urls import path
from . import views
from django.urls import re_path


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    re_path(r'^remove_cart_item/(?P<product_id>[0-9]+)/(?P<cart_item_id>[0-9]+)(?:/(?P<variation_id>[0-9]+))?/$', views.remove_cart_item, name='remove_cart_item'),
   
    path('checkout/', views.checkout, name='checkout'),
    path('cart/increment/<int:cart_item_id>/', views.increment_cart_item, name='increment_cart_item'),
    
]


