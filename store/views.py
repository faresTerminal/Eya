from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, Wishlist, ProductGallery, Coupon, Descriptions, Variation
from category.models import Category, SubCategory
from carts.models import CartItem
from django.db.models import Q
import random 
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from .forms import ReviewForm, CouponForm, SignboardForm
from django.contrib import messages
from django.db.models import Avg # when filter as top products(top rating)
from django.db import models
from django.db.models import Avg, Count, Prefetch



def store(request, category_slug=None, subcategory_slug = None):
    categories = None
    subcategories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        # Get variant information for each featured product
        variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
        )
        products = Product.objects.filter(category=categories, is_available=True).prefetch_related(variants_prefetch)
        
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    if subcategory_slug != None:
        subcategories = get_object_or_404(SubCategory, slug=subcategory_slug)
        products = products.filter(subcategory=subcategories)
       
    else:
        # Get variant information for each featured product
        variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
        )
        products = Product.objects.all().filter(is_available=True).order_by('-id').prefetch_related(variants_prefetch)
        
        
        paginator = Paginator(products, 8)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
        
     
    context = {
        'products': paged_products,
        
        'product_count': product_count,

    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug, subcategory_slug=None):
     # Get variant information for each featured product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )
    try:
        if subcategory_slug:
           single_product = Product.objects.get(category__slug=category_slug, subcategory__slug=subcategory_slug, slug=product_slug)
        else:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

   
   
    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    review_count = reviews.count()
    previous_product = Product.objects.filter(created_date__lt=single_product.created_date).last()
    next_product = Product.objects.filter(created_date__gt=single_product.created_date).first()
    all_products = Product.objects.all().order_by('id')[:5].prefetch_related(variants_prefetch)
    # Get the product gallery for single product
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id).order_by('id')[:4]
    descriptions = single_product.descriptions.all()
    galleries = single_product.galleries.all()
    
    
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
        
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)



def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


def wishlist(request):

    wishlist_items = Wishlist.objects.filter(user=request.user)
    
    context = {
    'wishlist_items': wishlist_items,
        }

    return render(request, 'store/wishlist.html', context)


def add_to_wishlist(request, product_id):
    # Check if the product is already in the wishlist
    product = Product.objects.get(id=product_id)
    if not Wishlist.objects.filter(user=request.user, product=product).exists():
        Wishlist.objects.create(user=request.user, product=product)
    
    return redirect('wishlist')


def remove_from_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    
    return redirect('wishlist')



def Featured_Products(request):

     # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )

    productss = Product.objects.annotate(cartitem_count=models.Count('cartitem'))
    featured_products = productss.order_by('-cartitem_count').prefetch_related(variants_prefetch)
    paginator = Paginator(featured_products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = featured_products.count()

    context = {
     'featured_products': paged_products,
     'product_count': product_count,
    }

    return render(request, 'store/featured_products.html', context)


def Top_Products(request):

     # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )

    top_products = Product.objects.annotate(average_rating=Avg('reviewrating__rating')).filter(
        average_rating__gt=0  # Only select products with a rating greater than 0
    ).order_by('-average_rating').prefetch_related(variants_prefetch)  # Order by highest average rating first

    paginator = Paginator(top_products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = top_products.count()

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

    paginator = Paginator(clearance_products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = clearance_products.count()

    context = {
     'clearance_products': paged_products,
     'product_count': product_count,
    }

    return render(request, 'store/clearance_products.html', context)



def products_by_category(request, category_slug, subcategory_slug=None):
     # Get variant information for each product
    variants_prefetch = Prefetch(
          'variations',
          queryset=Variation.objects.filter(is_active=True),
          to_attr='variants'
    )
    
    category = get_object_or_404(Category, category_name=category_slug)

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


