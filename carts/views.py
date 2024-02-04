from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation, Coupon
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from store.forms import CouponForm
from django.utils import timezone
# Create your views here.
from django.http import HttpResponse
from django.contrib import messages

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


 #https://www.ayocams.com/kristi_zenn/
   
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # get the product

    # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        variation_id = None  # Initialize variation_id to None

        if request.method == 'POST':
            color = request.POST.get('color')
            size = request.POST.get('size')

            try:
                # Check if both color and size are provided
                if color and size:
                    variation = Variation.objects.get(product=product, color__iexact=color, size__iexact=size)
                    product_variation.append(variation)
                    variation_id = variation.id
                elif color:
                    # Handle case where only color is provided
                    variation = Variation.objects.get(product=product, color__iexact=color)
                    product_variation.append(variation)
                    variation_id = variation.id
                elif size:
                    # Handle case where only size is provided
                    variation = Variation.objects.get(product=product, size__iexact=size)
                    product_variation.append(variation)
                    variation_id = variation.id
                else:
                    pass

            except Variation.DoesNotExist:
                pass

         # Check if variations exist or add product without variations
        if product_variation:
             is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variations__in=product_variation).exists()
        else:
             is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variations=None).exists()

        # Get quantity from the POST data
        quantity = int(request.POST.get('quantity', 1))

        if is_cart_item_exists:
            # If the cart item exists, increase the quantity
            cart_item = CartItem.objects.get(product=product, user=current_user, variation_id=variation_id)
            cart_item.quantity += quantity
            cart_item.save()

        else:
            # If the cart item does not exist, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                user=current_user,
                variation_id=variation_id  # Add variation_id here
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        # Update the variation quantities
        for variation in cart_item.variations.all():
            variation.quantity = max(0, variation.quantity - cart_item.quantity)
            variation.save()


        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        variation_id = None  # Initialize variation_id to None

        if request.method == 'POST':
            color = request.POST.get('color')
            size = request.POST.get('size')

            try:
                # Check if both color and size are provided
                if color and size:
                    variation = Variation.objects.get(product=product, color__iexact=color, size__iexact=size)
                    product_variation.append(variation)
                    variation_id = variation.id
                elif color:
                    # Handle case where only color is provided
                    variation = Variation.objects.get(product=product, color__iexact=color)
                    product_variation.append(variation)
                    variation_id = variation.id
                elif size:
                    # Handle case where only size is provided
                    variation = Variation.objects.get(product=product, size__iexact=size)
                    product_variation.append(variation)
                    variation_id = variation.id
                else:
                    pass

            except Variation.DoesNotExist:
                pass

         # Check if variations exist or add product without variations
        if product_variation:
             is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variations__in=product_variation).exists()
        else:
             is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user, variations=None).exists()

        # Get quantity from the POST data
        quantity = int(request.POST.get('quantity', 1))

        if is_cart_item_exists:
            # If the cart item exists, increase the quantity
            cart_item = CartItem.objects.get(product=product, user=current_user, variation_id=variation_id)
            cart_item.quantity += quantity
            cart_item.save()

        else:
            # If the cart item does not exist, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                user=current_user,
                variation_id=variation_id  # Add variation_id here
            )

            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()

        # Update the variation quantities
        for variation in cart_item.variations.all():
            variation.quantity = max(0, variation.quantity - cart_item.quantity)
            variation.save()


        return redirect('cart')
        

def remove_cart(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
           
            cart_item.delete()
    except:
        pass
    return redirect('cart')



def remove_cart_item(request, product_id, cart_item_id, variation_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    # Find the specific variation within the cart item
    variation = cart_item.variations.get(id=variation_id)

    # Adjust the variation quantity if needed
    variation.quantity = max(0, variation.quantity + cart_item.quantity)
    variation.save()

    # Remove the variation from the cart item
    cart_item.variations.remove(variation)

    # If there are no more variations in the cart item, delete the cart item
    if cart_item.variations.count() == 0:
        cart_item.delete()

    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    # Initialize variables
   
    grand_total = 0
    message = ""
   
    cart_item = None  # Initialize cart_item to None
    total_shipping_cost = 0

    try:
        # Fetch cart_items based on user authentication
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('-id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-id')

       
        # Check if cart_items is not empty
        if cart_items:
            for cart_item in cart_items:
                if cart_item.variations.exists():
            # Use variations.first() only if it's not None
                  first_variation = cart_item.variations.first()
                  if first_variation.clearance_price:
                     total += (first_variation.clearance_price * cart_item.quantity)
                  else:
                # Use clear_price or regular price based on your business logic
                     total += (first_variation.price * cart_item.quantity) if first_variation.price else 0

                  quantity += cart_item.quantity

               



            # Calculate shipping cost based on the number of cart items
            num_cart_items = len(cart_items)
            if num_cart_items == 1:
                total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
            else:
                total_shipping_cost = 600  # Set total_shipping_cost to 600 DA for more than one item

            grand_total = total + total_shipping_cost

    except ObjectDoesNotExist:
        pass  # Just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'total_shipping_cost': total_shipping_cost,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'message': message,
       
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        
        grand_total = 0
      
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

         # Check if cart_items is not empty
        if cart_items:
            for cart_item in cart_items:

                if cart_item.variations.exists() and cart_item.variations.first().clearance_price:
                    
                    total += (cart_item.variations.first().clearance_price * cart_item.quantity)
                    quantity += cart_item.quantity
                else:
                    
                    total += (cart_item.variations.first().price * cart_item.quantity)
                    quantity += cart_item.quantity

        
       
            # Calculate shipping cost based on the number of cart items
            num_cart_items = len(cart_items)
            if num_cart_items == 1:
                total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
            else:
                total_shipping_cost = 600  # Set total_shipping_cost to 600 DA for more than one item

            grand_total = total + total_shipping_cost
        


    except ObjectDoesNotExist:
        pass  # Just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        
        'total_shipping_cost': total_shipping_cost,
        'grand_total': grand_total,
       
    }

    return render(request, 'store/checkout.html', context)


