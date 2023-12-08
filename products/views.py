from django.shortcuts import render, redirect, get_object_or_404
from products.forms import ProductForm, VariantForm, GalleryImageForm, VariationtUpdateForm, DescriptionForm
from store.models import Product, Variation, ProductGallery, Descriptions
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.


def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.buyer = request.user
            # Set the currently logged-in user as the buyer
            product.save()
            return redirect('add_variants', product_id=product.id)
    else:
        product_form = ProductForm()
    return render(request, 'products/add_products.html', {'product_form': product_form})

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
    product = Product.objects.get(id=product_id)
    variants = Variation.objects.filter(product=product)
    if request.method == 'POST':
        variant_form = VariantForm(request.POST)
        if variant_form.is_valid():
            variant = variant_form.save(commit=False)
            variant.product = product
            
            variant.save()

            
            # Redirect back to the same product's variant addition page
            return HttpResponseRedirect(reverse('add_variants', args=[product_id]))
    else:
        variant_form = VariantForm()

    return render(request, 'products/add_variants.html', {'variant_form': variant_form, 'product': product, 'variants': variants})

def remove_variant(request, product_id, variant_id):
    product = get_object_or_404(Product, id=product_id)
    variant = get_object_or_404(Variation, id=variant_id)

    if request.method == 'POST':
        # Assuming you want to confirm the deletion with a POST request
        variant.delete()
        return redirect('add_variants', product_id=product_id)

    return render(request, 'products/remove_variant.html', {'product': product, 'variant': variant})






def add_gallery_images(request, product_id):
    product = Product.objects.get(id=product_id)
    variants = Variation.objects.filter(product=product)
    gallery = ProductGallery.objects.filter(product=product)
    if request.method == 'POST':
        gallery_image_form = GalleryImageForm(request.POST, request.FILES)
        if gallery_image_form.is_valid():
            gallery_image = gallery_image_form.save(commit=False)
            gallery_image.product = product
            gallery_image.save()
    else:
        gallery_image_form = GalleryImageForm()
    return render(request, 'products/add_gallery.html', {'gallery_image_form': gallery_image_form, 'product': product, 'gallery': gallery, 'variants': variants})

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

    context = {
        'user_products': user_products,
        'variation_clearance': variation_clearance,
    }

    return render(request, 'products/clearance_products.html', context)


def update_product(request, product_id):
    product = Variation.objects.get(id=product_id)
    

    if request.method == 'POST':
        form = VariationtUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            # Redirect to the product detail page or any other page as needed
            return redirect('list_clearance_products')

    else:
        form = VariationtUpdateForm(instance=product)

    context = {
        'product': product,
        'form': form,
    }

    return render(request, 'products/update_product.html', context)





def Management_Center(request):
    return render(request, 'products/management_center.html')

