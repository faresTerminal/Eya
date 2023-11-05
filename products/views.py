from django.shortcuts import render, redirect, get_object_or_404
from products.forms import ProductForm, VariantForm, GalleryImageForm, ProductUpdateForm, DescriptionForm
from store.models import Product, Variation, ProductGallery, Descriptions
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.


def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.buyer = request.user  # Set the currently logged-in user as the buyer
            product.save()
            return redirect('add_variants', product_id=product.id)
    else:
        product_form = ProductForm()
    return render(request, 'products/add_products.html', {'product_form': product_form})





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

    context = {
        'user_products': user_products,
    }

    return render(request, 'products/clearance_products.html', context)


def update_product(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        form = ProductUpdateForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            # Redirect to the product detail page or any other page as needed
            return redirect('product_detail', category_slug=product.category.slug, product_slug=product.slug)

    else:
        form = ProductUpdateForm(instance=product)

    context = {
        'product': product,
        'form': form,
    }

    return render(request, 'products/update_product.html', context)







