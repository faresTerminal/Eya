from django.urls import path
from . import views

urlpatterns = [
    path('promotions/', views.promotions, name='promotions'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('add-coupon/', views.add_coupon, name='add_coupon'),
    path('add-promotion/', views.add_promotion, name='add_promotion'),
]
