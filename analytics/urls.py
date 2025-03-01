from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
     
     path('', views.DashboardAnalytics, name='DashboardAnalytics'),
     path('product-viewer/', views.Product_Viewer, name='Product_Viewer'),
     path('product_profits/', views.Product_Profits, name='Product_Profits'),
     path('product_profits/<str:product_slug>/', views.Product_Profit_Detail, name='product_profit_detail'),
     path('costumer-sales/', views.Costumer_Sales, name='Costumer_Sales'),
     path('state-sales/', views.State_Sales, name='State_Sales'),
     path('product_profits/<str:product_slug>/<int:product_id>/', views.show_all_costumers_by_product, name='show_all_costumers_by_product'),
    
    
     
]
