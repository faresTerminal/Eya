from django.urls import path
from . import views




urlpatterns = [
    path('', views.store, name='store'),
     # URL for category only
    path('category/<slug:category_slug>/', views.products_by_category, name='products_by_category'),
    # URL for category and subcategory
    path('category/<slug:category_slug>/<slug:subcategory_slug>/', views.products_by_category, name='products_by_category'),
    #path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    #path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('products/<str:category_slug>/<str:product_slug>/', views.product_detail, name='product_detail'),
     # URL pattern for all products in a category (with subcategory)

   
    path('get_cities/', views.get_cities, name='get_cities'),
    path('product_list/', views.product_list, name='product_list'),
    

   

    # URL pattern for a specific product in a category (without subcategory)
    #path('category/<str:category_slug>/<str:product_slug>/', views.product_detail, name='product_detail_without_subcategory'),
    path('search/', views.search, name='search'),
    
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('features_products/', views.Featured_Products, name='Featured_Products'),
    path('top_products/', views.Top_Products, name='Top_Products'),
    path('clearance_products/', views.Clearance_Products, name='Clearance_Products'),

    path('create-signboard/', views.create_signboard, name='create_signboard'),
    path('create-deal-and-outlet/', views.create_deals_and_outlet, name='create_deals_and_outlet'),
    
    

   
   


   
]
