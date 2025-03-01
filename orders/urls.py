from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
     
     path('place_order/', views.place_order, name='place_order'),
    
     #path('order_complete/', views.order_complete, name='order_complete'),
     path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
     path('success/<str:transaction_id>/', views.payment_success, name='payment_success'),
     #path('invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
     path('invoice/<str:transaction_id>/', views.view_invoice, name='view_invoice'),
     path('invoice/download/<str:transaction_id>/', views.download_invoice, name='download_invoice'),
     path('digital_product/<slug:product_slug>/download/', views.download_product, name='download_product'),
     path('downloads/', views.download_purchase, name='download_purchase'),
     path('remove_download/<int:order_id>/', views.remove_download, name='remove_download'),
    
]