from django.shortcuts import render
from django.db.models import Avg 
from store.models import Product, Daily_slide, Signboard, ReviewRating, Variation, Daily_and_Outlet
from carts.models import CartItem
from marketing.models import Promotion, Coupon
from accounts.models import Shop_Social
from django.shortcuts import redirect
from django.utils.translation import activate
from django.utils.translation import gettext_lazy as _
from blog.models import Article
from django.db.models import Count
from django.utils import timezone
from django.db import models
from django.db.models import Avg, Count, Prefetch
from chat.models import Message, Conversation
from category.models import Category
from orders.models import OrderProduct
from django.db.models import Sum, Count
from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from publicite.models import Advertisement
import random

from publicite.models import SlideAd, ShowAd

def some_view(request):
    cookies_accepted = request.COOKIES.get("cookies_accepted", "false")
    if cookies_accepted == "true":
        # Load personalized features or analytics
        pass
    return render(request, "homebase.html")


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
    clearance_products = Product.objects.filter(is_clearance=True).order_by('-id')[:1].prefetch_related(variants_prefetch)

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


    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()

    )
    active_coupons = Coupon.objects.filter(is_active=True)


    # Fetch conversations with unread messages for the current user (either as buyer or seller)
    unread_conversations = Conversation.objects.none()  # Default to an empty queryset for anonymous users

    if request.user.is_authenticated:
       unread_conversations = Conversation.objects.filter(
        (models.Q(buyer=request.user) | models.Q(seller=request.user)),
        messages__is_read=False
       ).distinct()

    unread_messages_count = unread_conversations.count()


    # Define categories and filter products by each category
    categorys = {
        'all': Product.objects.filter(is_available=True),
        'Electronic': Product.objects.filter(category__category_name="Electronic", is_available=True),
        'Fashion': Product.objects.filter(category__category_name="Fashion", is_available=True),
        'Home': Product.objects.filter(category__category_name="Home & Kitchen", is_available=True),
        'Beauty': Product.objects.filter(category__category_name="Beauty & Personal Care", is_available=True),
        'Health & Wellness': Product.objects.filter(category__category_name="Health & Wellness", is_available=True),
        
       
        'Books & Media': Product.objects.filter(category__category_name="Books & Media", is_available=True),
        'Automotive': Product.objects.filter(category__category_name="Automotive", is_available=True),
    }

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
        'categorys': categorys,
        'active_promotions': active_promotions,
        'active_coupons': active_coupons,
        'unread_messages_count': unread_messages_count,
        'unread_conversations': unread_conversations,
    }

    # Render the 'home.html' template with the defined context
    return render(request, 'home.html', context)


def home2(request):
    
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


    recommendadion = Product.objects.all().order_by('-id')[:8].prefetch_related(variants_prefetch)
    # Retrieve the first 2 clearance items ordered by ID and the last 2 clearance items ordered by ID
    clearance1 = Product.objects.all().filter(is_clearance=True).order_by('id')[:2].prefetch_related(variants_prefetch)
    clearance2 = Product.objects.all().filter(is_clearance=True).order_by('-id')[:2].prefetch_related(variants_prefetch)

    # Retrieve the first 3 daily slides that are not the deal of the day
    daily_slide = Daily_slide.objects.prefetch_related(
      Prefetch(
        'product__variations',  # Access 'variations' through 'product'
        queryset=Variation.objects.filter(is_active=True),
        to_attr='active_variations'  # Prefetch to 'active_variations'
      )
    ).order_by('-id')

    # Retrieve the latest signboard for the 'Signboard' section
    signboard = Signboard.objects.prefetch_related(
      Prefetch(
        'product__variations',  # Access 'variations' through 'product'
        queryset=Variation.objects.filter(is_active=True),
        to_attr='active_variations'  # Prefetch to 'active_variations'
      )
    ).order_by('-id')[:1]

    # Check if there are active deals in the 'Deals Outlet' section
    deals_outlet = Daily_slide.objects.filter(expiration_time__gt=timezone.now()).order_by('id')[:2]
    if deals_outlet.exists():
        # Deals are still valid, show the first two clearance items
        clearance1 = Product.objects.all().filter(is_clearance=True).order_by('id')[:2].prefetch_related(variants_prefetch)
    else:
        # Deals have expired, show the first four clearance items
        clearance2 = Product.objects.all().filter(is_clearance=True).order_by('-id')[:2].prefetch_related(variants_prefetch)
    daily_and_outlet = Daily_and_Outlet.objects.filter(expiration_time__gt=timezone.now()).prefetch_related(
      Prefetch(
        'product__variations',  # Access 'variations' through 'product'
        queryset=Variation.objects.filter(is_active=True),
        to_attr='active_variations'  # Prefetch to 'active_variations'
      )
    ).order_by('-id')[:2]
    # Retrieve all shop social media links
    shop_social = Shop_Social.objects.all()

    # Retrieve the top-rated product based on average rating
    top_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating')[:1].prefetch_related(variants_prefetch)

    # Retrieve the latest clearance product
    clearance_products = Product.objects.filter(is_clearance=True).order_by('-id')[:1].prefetch_related(variants_prefetch)

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


    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()

    )
    active_coupons = Coupon.objects.filter(is_active=True)


    # Fetch conversations with unread messages for the current user (either as buyer or seller)
    unread_conversations = Conversation.objects.none()  # Default to an empty queryset for anonymous users

    if request.user.is_authenticated:
       unread_conversations = Conversation.objects.filter(
        (models.Q(buyer=request.user) | models.Q(seller=request.user)),
        messages__is_read=False
       ).distinct()

    unread_messages_count = unread_conversations.count()

    """Home page view that includes advertisements."""
    active_ads = Advertisement.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    ad = random.choice(active_ads) if active_ads.exists() else None  # Pick a random ad

   


    # Define categories and filter products by each category
    categorys = {
        'all': Product.objects.filter(is_available=True),
        'Electronic': Product.objects.filter(category__category_name="Electronic", is_available=True),
        'Fashion': Product.objects.filter(category__category_name="Fashion", is_available=True),
        'Home': Product.objects.filter(category__category_name="Home & Kitchen", is_available=True),
        'Beauty': Product.objects.filter(category__category_name="Beauty & Personal Care", is_available=True),
        'Health & Wellness': Product.objects.filter(category__category_name="Health & Wellness", is_available=True),
        
       
        'Books & Media': Product.objects.filter(category__category_name="Books & Media", is_available=True),
        'Automotive': Product.objects.filter(category__category_name="Automotive", is_available=True),
    }

    category = Category.objects.all().order_by('-id')[:6]
    

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
        'categorys': categorys,
        'active_promotions': active_promotions,
        'active_coupons': active_coupons,
        'unread_messages_count': unread_messages_count,
        'unread_conversations': unread_conversations,
        'category': category,
        'daily_and_outlet': daily_and_outlet,
        'recommendadion': recommendadion,
        'active_ads': active_ads,
        'ad': ad,
       
        
    }

    # Render the 'home.html' template with the defined context
    return render(request, 'home2.html', context)

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



