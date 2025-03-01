from django.urls import path
from . import views


urlpatterns = [
     path('', views.stock, name='stock'),
     path('product_list_stock/', views.product_list_stock, name='product_list_stock'),
     path('stock-adjustment/<int:product_id>/', views.stock_adjustment, name='stock_adjustment'),
     path('stock_adjust_page/', views.stock_adjust_page, name='stock_adjust_page'),
     path('low_stock/', views.low_stock, name='low_stock'),
     path('stock_valuation/', views.stock_valuation, name='stock_valuation'),
     path('stock-history/', views.stock_history, name='stock_history'),
     path('update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
     
     #path('stock-sammary/', views.stock_sammary, name='stock_sammary'),
    
     
    
]