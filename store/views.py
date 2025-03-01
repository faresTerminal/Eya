from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, Wishlist, ProductGallery, Coupon, Descriptions, Variation, Color
from category.models import Category, SubCategory
from carts.models import CartItem
from django.db.models import Q
import random 
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, JsonResponse
from .forms import ReviewForm, CouponForm, SignboardForm, DealsAndOutletForm
from django.contrib import messages
from django.db.models import Avg # when filter as top products(top rating)
from django.db import models
from django.db.models import Avg, Count, Prefetch
from django.utils import timezone
# Import the Counter class from the collections module
from collections import Counter
from django.contrib.auth.decorators import login_required
from orders.models import City
from social.models import FacebookPixel
from seo.models import Metadata, ContentType
from publicite.models import Advertisement, SlideAd, ShowAd
from analytics.models import ProductView


def store(request, category_slug=None, subcategory_slug=None):
    categories = None
    subcategories = None
    products = None
    current_time = timezone.now()

    # Get selected filters from request
    category_filter = request.GET.getlist('category')
    size_filter = request.GET.getlist('size')
    color_filter = request.GET.getlist('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Handle category filter
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        # Prefetch variations for active variants
        variants_prefetch = Prefetch(
            'variations',
            queryset=Variation.objects.filter(is_active=True),
            to_attr='variants'
        )
        products = Product.objects.filter(category=categories, is_available=True).prefetch_related(variants_prefetch)

    # Handle subcategory filter
    if subcategory_slug != None:
        subcategories = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=subcategories)
    
    else:
        # Default: Get all available products (no category or subcategory filter)
        variants_prefetch = Prefetch(
            'variations',
            queryset=Variation.objects.filter(is_active=True),
            to_attr='variants'
        )
        products = Product.objects.filter(is_available=True).order_by('-id').prefetch_related(variants_prefetch)

    # Apply filters on variations model (size, color, price)
    if category_filter:
        products = products.filter(category__slug__in=category_filter)

    if size_filter:
        # Filter based on variations related to size
        products = products.filter(variations__size__in=size_filter)

    if color_filter:
        # Filter based on variations related to color
        products = products.filter(variations__color__hex_code__in=color_filter)

    if min_price and max_price:
        # Filter based on the price range in the variations model
        products = products.filter(variations__price__gte=min_price, variations__price__lte=max_price)

    # Pagination logic
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    # Adding the 'is_new' attribute based on the creation date
    for product in paged_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    # Get all filter options for the sidebar
    categories = Category.objects.all()
    colors = Color.objects.all()
    sizes = Variation.objects.values_list('size', flat=True).distinct()

    """Home page view that includes advertisements."""
    active_ads = Advertisement.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    slide_ads = SlideAd.objects.filter(is_active=True)
    show_ads = ShowAd.objects.filter(is_active=True)

   

    context = {
        'products': paged_products,
        'product_count': product_count,
        'categories': categories,
        'colors': colors,
        'sizes': sizes,
        'category_slug': category_slug,
        'subcategory_slug': subcategory_slug,
        'active_ads': active_ads,
        'slide_ads': slide_ads,
        'show_ads': show_ads,

    }

    return render(request, 'store/store.html', context)

from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

def product_detail(request, category_slug, product_slug, subcategory_slug=None):
    current_time = now()

    # Prefetch variant information
    variants_prefetch = Prefetch(
        'variations',
        queryset=Variation.objects.filter(is_active=True),
        to_attr='variants'
    )

    try:
        # Fetch the product based on category and slug
        if subcategory_slug:
            single_product = Product.objects.get(category__slug=category_slug, subcategory__slug=subcategory_slug, slug=product_slug)
        else:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        
        # Check if the product is in the cart
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Product.DoesNotExist:
        # Handle case where the product does not exist
        return render(request, 'store/404.html', status=404)

    # Save the page view for this product
    ip_address = request.META.get('REMOTE_ADDR')
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None  # Anonymous user
    
    ProductView.objects.create(
        product=single_product,
        user=user,
        ip_address=ip_address
    )

    # Fetch reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    review_count = reviews.count()

    # Fetch related products
    previous_product = Product.objects.filter(created_date__lt=single_product.created_date).last()
    next_product = Product.objects.filter(created_date__gt=single_product.created_date).first()
    all_products = Product.objects.all().order_by('-id').prefetch_related(variants_prefetch)[:5]

    # Fetch product gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id).order_by('id')[:4]
    descriptions = single_product.descriptions.all()
    galleries = single_product.galleries.all()

    # Update 'is_new' attribute for related products
    for product in all_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    # Get unique colors and associated data
    unique_colors_data = []
    for variation in single_product.variations.all():
        if variation.color and not any(color_data['color'] == variation.color for color_data in unique_colors_data):
            unique_colors_data.append({
                'color': variation.color,
                'size': variation.size,
                'price': variation.clearance_price if variation.clearance_price else variation.price,
                'quantity': variation.quantity,
            })

    # Fetch metadata
    metadata = Metadata.objects.filter(
        content_type=ContentType.objects.get_for_model(single_product),
        object_id=single_product.id
    ).first()

    

    # Prepare context
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'reviews': reviews,
        'review_count': review_count,
        'descriptions': descriptions,
        'previous_product': previous_product,
        'next_product': next_product,
        'all_products': all_products,
        'product_gallery': product_gallery,
        'galleries': galleries,
        'unique_colors_data': unique_colors_data,
        'metadata': metadata,
        

    }

    return render(request, 'store/product_detail.html', context)





from django.db.models import Q

def search(request):
    products = Product.objects.none()  # Initialize an empty queryset
    product_count = 0

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        
        if keyword and keyword.startswith('@'):
            # Remove the '@' symbol from the keyword to search for the username
            keyword = keyword[1:]  # Strips the '@' symbol from the beginning

            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) |
                Q(product_name__icontains=keyword) |
                Q(subcategory__name__icontains=keyword) |  # Search in SubCategory name
                Q(subcategory__category__category_name__icontains=keyword) |  # Search in Category name
                Q(buyer__username__icontains=keyword)  # Search in buyer's username
            )
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)





# Ensure Notification is imported

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')  # Get the URL to redirect back after submission

    if request.method == 'POST':
        # Check if the user has already reviewed the product
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')

            # Notification for review update
            profile_picture_url = (
                request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'
            )
            Notification.objects.create(
                sender=request.user,
                recipient=reviews.product.buyer,  # Assuming the recipient is the user updating the review
                message=f"You have updated your review for \n'{reviews.product.product_name}'.",
                url=f"/store/products/{reviews.product.category.slug}/{reviews.product.slug}",  # Redirect to the product detail page
                profile_picture_url=profile_picture_url
            )

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                # Create a new review
                data = form.save(commit=False)  # Save the form data without committing yet
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()

                messages.success(request, 'Thank you! Your review has been submitted.')

                # Notification for new review
                profile_picture_url = (
                    request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'
                )
                Notification.objects.create(
                    sender=request.user,
                    recipient=data.product.buyer,  # Assuming the recipient is the user who submitted the review
                    message=f"You have submitted a review for\n '{data.product.product_name}'.",
                    url=f"/store/products/{data.product.category.slug}/{data.product.slug}",  # Redirect to the product detail page
                    profile_picture_url=profile_picture_url
                )

        return redirect(url)

    # If the request method is not POST, redirect back
    return redirect(url)





def wishlist(request):

    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
    'wishlist_items': wishlist_items,
        }

    return render(request, 'store/wishlist.html', context)


from notification.models import Notification  # Ensure Notification is imported

def add_to_wishlist(request, product_id):
    # Get the product or return a 404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Check if the product is already in the wishlist
    if not Wishlist.objects.filter(user=request.user, product=product).exists():
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, 'Product Added To Your Wishlist')

        # Retrieve the user's profile picture URL
        profile_picture_url = (
            request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'
        )

        # Send a notification to the user
        Notification.objects.create(
            sender=request.user,
            recipient=product.buyer,  # Assuming the recipient is the user adding the product
            message=f"added '{product.product_name}' to wishlist.",
            url=f"/store/wishlist/",  # Redirect to the wishlist page or the product detail page
            profile_picture_url=profile_picture_url  # Save the profile picture URL in the notification
        )
    else:
        messages.warning(request, 'Product is already in your Wishlist')

    return redirect('wishlist')


def remove_from_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.error(request, 'Product Removed From Your Wishlist')
    return redirect('wishlist')



def Featured_Products(request):

    current_time = timezone.now()

     # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )

    productss = Product.objects.annotate(cartitem_count=models.Count('cartitem'))
    featured_products = productss.order_by('-cartitem_count').prefetch_related(variants_prefetch)
    paginator = Paginator(featured_products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = featured_products.count()

    # to dispaly product if new or not
    for product in paged_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    context = {
     'featured_products': paged_products,
     'product_count': product_count,
    }

    return render(request, 'store/featured_products.html', context)


def Top_Products(request):

    current_time = timezone.now()

     # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )

    top_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating').prefetch_related(variants_prefetch)  # Order by highest average rating first

    paginator = Paginator(top_products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = top_products.count()

     # to dispaly product if new or not
    for product in paged_products:
        time_difference = current_time - product.created_date
        product.is_new = time_difference.days == 0

    context = {
     'top_products': paged_products,
     'product_count': product_count,
    }

    return render(request, 'store/top_products.html', context)


def Clearance_Products(request):

    # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )

    clearance_products = Product.objects.filter(is_clearance =True).order_by('-id').prefetch_related(variants_prefetch)  # Order by highest average rating first

    paginator = Paginator(clearance_products, 12)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = clearance_products.count()

    context = {
     'clearance_products': paged_products,
     'product_count': product_count,
    }

    return render(request, 'store/clearance_products.html', context)



def products_by_category(request, category_slug, subcategory_slug=None):
    # Fetch the category by its slug
    category = get_object_or_404(Category, slug=category_slug)

    # Prefetch related active variations
    variants_prefetch = Prefetch(
        'variations',
        queryset=Variation.objects.filter(is_active=True),
        to_attr='variants'
    )

    # Check if a subcategory is provided
    if subcategory_slug:
        subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, category=category)
        products = Product.objects.filter(category=category, subcategory=subcategory, is_available=True).prefetch_related(variants_prefetch)
    else:
        products = Product.objects.filter(category=category, is_available=True).prefetch_related(variants_prefetch)

    context = {
        'products': products,
        'category': category,
    }

    if subcategory_slug:
        context['subcategory'] = subcategory

    return render(request, 'store/products_by_category.html', context)






def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")



def create_signboard(request):
    curren_user = request.user
    product = Product.objects.filter(buyer = curren_user)
    if request.method == 'POST':
        form = SignboardForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Signboard created successfully!')
            return redirect('Management_Center')  # Replace with the URL or name of the success page
    else:
        form = SignboardForm()

    return render(request, 'products/add_signboard.html', {'form': form, 'product': product})


def create_deals_and_outlet(request):
    curren_user = request.user
    product = Product.objects.filter(buyer = curren_user)
    if request.method == 'POST':
        form = DealsAndOutletForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deal and Outlet created successfully!')
            return redirect('Management_Center')  # Replace with the URL or name of the success page
    else:
        form = DealsAndOutletForm()

    return render(request, 'products/add_deal_and_outlet.html', {'form': form, 'product': product})

#this function to get cities for etch Stete
def get_cities(request):
    # Get the state ID from the query string
    state_id = request.GET.get('state_id')
    print('id', state_id)

    if state_id:
        # Fetch cities that belong to the selected state
        cities = City.objects.filter(state_id=state_id)
        cities_data = [{"id": city.id, "name": city.name} for city in cities]

        return JsonResponse(cities_data, safe=False)
    else:
        return JsonResponse([], safe=False)


def product_list(request):
    # Get selected filters from request
    category_filter = request.GET.getlist('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Start with filtering the Variation model
    variations = Variation.objects.all()

    # Filter by category (on the Product model through Variation)
    if category_filter:
        variations = variations.filter(product__category__slug__in=category_filter)

   

   

    # Filter by price range (on the Variation model)
    if min_price and max_price:
        variations = variations.filter(price__gte=min_price, price__lte=max_price)

    # Get unique product IDs from the filtered variations
    product_ids = variations.values_list('product_id', flat=True).distinct()

    # Now filter the products based on the selected variations
    products = Product.objects.filter(id__in=product_ids)

    # Get all filter options for the sidebar
    categories = Category.objects.all()
   

    context = {
        'products': products,
        'categories': categories,
        
    }

    return render(request, 'store/store.html', context)




