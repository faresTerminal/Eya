from django.shortcuts import render
from django.db.models import Avg 
from store.models import Product, Daily_slide, Signboard, ReviewRating, Variation
from carts.models import CartItem

from accounts.models import Shop_Social
from django.shortcuts import redirect
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from blog.models import Article
from django.db.models import Count
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Count, Prefetch






def home(request):
    
    #lang_code = request.GET.get('lang', 'en')  # Default to English if no language specified
    #activate(lang_code)
    # To make the 'NEW' label hide after 1 day
    current_time = timezone.now()

    # Get variant information for each featured product
    variants_prefetch = Prefetch(
        'variations',
        queryset=Variation.objects.filter(is_active=True),
        to_attr='variants'
    )

    # Retrieve all available products and prefetch related variant information
    products = Product.objects.all().filter(is_available=True).prefetch_related(variants_prefetch)

    # Annotate product queryset with the count of related cart items
    productss = Product.objects.annotate(cartitem_count=models.Count('cartitem'))

    # Retrieve featured products ordered by the count of related cart items
    featured_products = productss.order_by('-cartitem_count').prefetch_related(variants_prefetch)

    # Retrieve the latest 5 products for the 'On Sale' section
    on_sale = Product.objects.all().order_by('-id')[:5].prefetch_related(variants_prefetch)

    # Retrieve the latest 3 blog articles for the 'On Blog' section
    on_blog = Article.objects.all().order_by('-id')[:3]

    # Retrieve top-rated products based on average rating
    top_rated_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating').prefetch_related(variants_prefetch)

    # Retrieve the first 2 clearance items ordered by ID and the last 2 clearance items ordered by ID
    clearance1 = Product.objects.all().filter(is_clearance=True).order_by('id')[:2].prefetch_related(variants_prefetch)
    clearance2 = Product.objects.all().filter(is_clearance=True).order_by('-id')[:2].prefetch_related(variants_prefetch)

    # Retrieve the first 3 daily slides that are not the deal of the day
    daily_slide = Daily_slide.objects.all().filter(deal_of_day=False).order_by('id')[:3]

    # Retrieve the latest signboard for the 'Signboard' section
    signboard = Signboard.objects.all().order_by('-id')[:1]

    # Check if there are active deals in the 'Deals Outlet' section
    deals_outlet = Daily_slide.objects.filter(expiration_time__gt=timezone.now()).order_by('id')[:1]
    if deals_outlet.exists():
        # Deals are still valid, show the first two clearance items
        clearance1 = Product.objects.all().filter(is_clearance=True).order_by('id')[:2].prefetch_related(variants_prefetch)
    else:
        # Deals have expired, show the first four clearance items
        clearance2 = Product.objects.all().filter(is_clearance=True).order_by('-id')[:2].prefetch_related(variants_prefetch)

    # Retrieve all shop social media links
    shop_social = Shop_Social.objects.all()

    # Retrieve the top-rated product based on average rating
    top_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating')[:1]

    # Retrieve the latest clearance product
    clearance_products = Product.objects.filter(is_clearance=True).order_by('-id')[:1]

    # Update the products in the 'Featured Products', 'On Sale', and 'Top Rated Products' sections
    # to include an 'is_new' attribute based on the creation date
    for product in featured_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    for product in on_sale:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    for product in top_rated_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    # Retrieve the most featured product for the 'Featured Banner' section
    featured_banner = productss.order_by('-cartitem_count')[:1]

    # Define the context with all the retrieved data
    context = {
        'products': products,
        'featured_banner': featured_banner,
        'top_products': top_products,
        'clearance_products': clearance_products,
        'featured_products': featured_products,
        'top_rated_products': top_rated_products,
        'on_sale': on_sale,
        'daily_slide': daily_slide,
        'signboard': signboard,
        'deals_outlet': deals_outlet,
        'clearance1': clearance1,
        'clearance2': clearance2,
        'shop_social': shop_social,
        'on_blog': on_blog,
    }

    # Render the 'home.html' template with the defined context
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

