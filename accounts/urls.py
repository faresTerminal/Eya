from django.urls import path
from . import views






urlpatterns = [
   
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('register_confirme_link/', views.register_confirme_link, name='register_confirme_link'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    path('', views.dashboard, name='dashboard'),
   

    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),


    path('my_orders/', views.my_orders, name='my_orders'),
   
    path('printing/', views.printing, name='printing'),
    path('User_Products/', views.User_Products, name='User_Products'),
    # remove a product
    path('products/<int:product_id>/remove/', views.remove_product, name='remove_product'),

    path('remove_completed_orders/<int:order_id>', views.remove_completed_orders, name='remove_completed_orders'),
    # list of products removed
    path('Product_Removed/', views.remove_product, name='remove_product'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
]


