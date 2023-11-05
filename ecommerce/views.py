from django.shortcuts import render
from django.db.models import Avg 
from store.models import Product, Daily_slide, Signboard, ReviewRating
from carts.models import CartItem
from django.utils import timezone
from accounts.models import Shop_Social
from django.shortcuts import redirect
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from blog.models import Article
from django.db.models import Count
from django.utils import timezone
from django.db import models

def home(request):
    #to make element NEW hide after 1 day
    current_time = timezone.now()

    products = Product.objects.all().filter(is_available=True)
   
    
    productss = Product.objects.annotate(cartitem_count=models.Count('cartitem'))
    featured_products = productss.order_by('-cartitem_count')
    
    on_sale = Product.objects.all().order_by('-id')[:5]
    on_blog = Article.objects.all().order_by('-id')[:3]
    top_rated_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating')  # Order by highest average rating first
    clearance = Product.objects.all().filter(is_clearance =True).order_by('-id')[:2]
    daily_slide = Daily_slide.objects.all().filter(deal_of_day = False).order_by('id')[:3]
    signboard = Signboard.objects.all().order_by('-id')[:1]
    deals_outlet = Daily_slide.objects.filter(expiration_time__gt=timezone.now()).order_by('id')[:1]
    shop_social = Shop_Social.objects.all()
    top_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating')[:1]  # Order by highest average rating first
    clearance_products = Product.objects.filter(is_clearance =True).order_by('-id')[:1]

    # Update the products to include a 'is_new' attribute based on the creation date
    for product in featured_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    #featured banner
    productss = Product.objects.annotate(cartitem_count=models.Count('cartitem'))
    featured_banner = productss.order_by('-cartitem_count')[:1]
   

    context = {
        'products': products,
        'featured_banner': featured_banner,
        'top_products': top_products,
        'clearance_products': clearance_products,
        'featured_products': featured_products,
        'top_rated_products': top_rated_products,
        'on_sale': on_sale,
        'clearance': clearance,
        'daily_slide': daily_slide,
        'signboard': signboard,
        'deals_outlet': deals_outlet,
        'shop_social': shop_social,
        'on_blog': on_blog,
        
       

    }
    return render(request, 'home.html', context)





def custom_404(request, exception):
    context = {
        "error_message": "We are sorry, the page you've requested is not available."
    }
    return render(request, 'includes/404.html', context, status=404)



# function for server Error 500
def server_error(request):
    context = {
        "error_message": "Sorry, we're experiencing technical difficulties. Please try again later, or you may be using a proxy."
    }
    return render(request, 'accounts/500.html', context, status=500)

