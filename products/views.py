from django.shortcuts import render, redirect, get_object_or_404
from products.forms import ProductForm, VariantForm, GalleryImageForm, VariationtUpdateForm, DescriptionForm
from store.models import Product, Variation, ProductGallery, Descriptions, Color
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
# Create your views here.


from django.contrib.auth import get_user_model
from notification.models import Notification



  # Import the necessary models


from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.buyer = request.user  # Set the currently logged-in user as the buyer

            # Handle digital products (if the product is digital, you might upload a file instead of images)
            if product.product_type == Product.DIGITAL:
                # If it's a digital product, save the digital file (optional, depending on your model)
                digital_file = request.FILES.get('digital_file')  # Retrieve the digital file uploaded by the user
                if digital_file:
                    product.digital_file = digital_file  # You should have a 'digital_file' field in your model

            product.save()  
          # Save the product first
            
            # Send notifications to all users (excluding the sender)
            try:
                User = get_user_model()
                all_users = User.objects.exclude(id=request.user.id)  # Exclude the user who added the product

                # Get the sender's profile picture URL
                profile_picture_url = (
                    product.buyer.userprofile.profile_picture.url if product.buyer.userprofile.profile_picture
                    else '/static/default_profile_picture.png'  # Default profile picture if none exists
                )

                # Show only the first 6 words with "..." if the product name has more than 6 words
                product_name_words = product.product_name.split()
                if len(product_name_words) > 6:
                    product_name_display = ' '.join(product_name_words[:6]) + '...'
                else:
                    product_name_display = product.product_name

                for user in all_users:
                    Notification.objects.create(
                        sender=request.user,
                        recipient=user,
                        message=f"A new product \n'{product_name_display}'\n has been added.",
                        url=f"/store/products/{product.category.slug}/{product.slug}/",  # Redirect to the product detail page
                        profile_picture_url=profile_picture_url  # Include the profile picture URL
                    )
            except Exception as e:
                # Log the error message or handle it as needed
                print(f"Failed to create notification: {e}")

            # Redirect to add_variants after notifications are sent
            return redirect('add_variants', product_id=product.id)
    else:
        product_form = ProductForm()
    
    return render(request, 'products/add_products.html', {'product_form': product_form})


# File upload handler (optional)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage

@csrf_exempt
def file_upload(request):
    if request.method == 'POST' and request.FILES.get('digital_file'):
        digital_file = request.FILES['digital_file']
        fs = FileSystemStorage()
        filename = fs.save(digital_file.name, digital_file)
        return JsonResponse({'message': 'File uploaded successfully'})
    return JsonResponse({'error': 'No file uploaded'}, status=400)


def edit_product(request, product_id):
    # Retrieve the product instance
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        if product_form.is_valid():
            edited_product = product_form.save(commit=False)
            edited_product.buyer = request.user  # Set the currently logged-in user as the buyer
            edited_product.save()
             # Redirect to the user's product page
            return HttpResponseRedirect(reverse('add_variants', args=[product_id]))
    else:
        product_form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'product_form': product_form, 'product': product})




def add_variants(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = Variation.objects.filter(product=product)
    colors = Color.objects.all()

    if request.method == 'POST':
        variant_form = VariantForm(request.POST)
        
        if variant_form.is_valid():
            variant = variant_form.save(commit=False)
            variant.product = product
            variant.save()  # Save the variant after setting the product
            # Redirect back to the same product's variant addition page
            return HttpResponseRedirect(reverse('add_variants', args=[product_id]))
    else:
        variant_form = VariantForm()

    return render(request, 'products/add_variants.html', {
        'variant_form': variant_form,
        'product': product,
        'variants': variants,
        'colors': colors,
    })



def remove_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id)
    variant = get_object_or_404(Variation, id=variant_id)

    if request.method == 'POST':
        # Assuming you want to confirm the deletion with a POST request
        variant.delete()
        return redirect('add_variants', product_id=product_id)

    return render(request, 'products/remove_variant.html', {'product': product, 'variant': variant})






# views.py



def add_gallery_images(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = Variation.objects.filter(product=product)
    gallery = ProductGallery.objects.filter(product=product)

    # Check if there is any gallery image with a youtube_url
    has_youtube_url = product.galleries.filter(youtube_url__isnull=False).exists()

    if request.method == 'POST':
        gallery_image_form = GalleryImageForm(request.POST, request.FILES)
        
        if gallery_image_form.is_valid():
            gallery_image = gallery_image_form.save(commit=False)
            gallery_image.product = product
            gallery_image.save()

            return render(request, 'products/add_gallery.html', {
                'gallery_image_form': gallery_image_form, 
                'product': product, 
                'gallery': gallery, 
                'variants': variants,
                'has_youtube_url': has_youtube_url,  # Pass the flag to template
                'message': 'Gallery image/video added successfully!'
            })
        else:
            return render(request, 'products/add_gallery.html', {
                'gallery_image_form': gallery_image_form, 
                'product': product, 
                'gallery': gallery, 
                'variants': variants,
                'has_youtube_url': has_youtube_url,  # Pass the flag to template
                'message': 'There was an error in the form submission.'
            })

    else:
        gallery_image_form = GalleryImageForm()

    return render(request, 'products/add_gallery.html', {
        'gallery_image_form': gallery_image_form,
        'product': product,
        'gallery': gallery,
        'variants': variants,
        'has_youtube_url': has_youtube_url  # Pass the flag to template
    })




def remove_gallery_image(request, product_id, image_id):
    product = get_object_or_404(Product, id=product_id)
    image = get_object_or_404(ProductGallery, id=image_id)

    if request.method == 'POST':
        # Assuming you want to confirm the deletion with a POST request
        image.delete()
        return redirect('add_gallery_images', product_id=product_id)

    return render(request, 'products/remove_gallery_image.html', {'product': product, 'image': image})

def add_description(request, product_id):
    product = Product.objects.get(id=product_id)
    variants = Variation.objects.filter(product=product)
    gallery = ProductGallery.objects.filter(product=product)
    description = Descriptions.objects.filter(product=product)
    if request.method == 'POST':
        description_form = DescriptionForm(request.POST)
        if description_form.is_valid():
            descrip = description_form.save(commit=False)
            descrip.product = product
            descrip.save()
    else:
        description_form = DescriptionForm()
    return render(request, 'products/description.html', {'description_form': description_form, 'product': product, 'gallery': gallery, 'variants': variants})


def list_clearance_products(request):
    
    user = request.user  
    user_products = Product.objects.filter(buyer=user)
    variation_clearance = Variation.objects.filter(product__in = user_products)

    paginator = Paginator(variation_clearance, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = variation_clearance.count()

    context = {
        'user_products': user_products,
        'variation_clearance': paged_products,
    }

    return render(request, 'products/clearance_products.html', context)


def update_product(request, product_id):
    variation = Variation.objects.get(id=product_id)

    if request.method == 'POST':
        form = VariationtUpdateForm(request.POST, instance=variation)
        if form.is_valid():
            form.save()

            # Update is_clearance field in the associated Product
            variation.product.is_clearance = variation.is_active
            variation.product.save()

            # Redirect to the product list page or any other page as needed
            return redirect('list_clearance_products')

    else:
        form = VariationtUpdateForm(instance=variation)

    context = {
        'product': variation,
        'form': form,
    }

    return render(request, 'products/update_product.html', context)







def Management_Center(request):
    return render(request, 'products/management_center.html')

