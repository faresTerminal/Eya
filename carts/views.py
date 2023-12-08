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


 
   
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
   # If the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            color = request.POST.get('color')
            size = request.POST.get('size')
           

            

            try:
                variation = Variation.objects.get(product=product, color__iexact=color, size__iexact=size)
                product_variation.append(variation)


            except Variation.DoesNotExist:
                pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        # Get quantity from the POST data
        quantity = int(request.POST.get('quantity', 1))
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += quantity
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=quantity, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = quantity,
                user = current_user,
                
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        cart_item = CartItem.objects.filter(product=product, user=current_user)
        for item in cart_item:
             for variation in item.variations.all():
              variation.quantity = max(0, variation.quantity - item.quantity)
              variation.save()


        return redirect('cart')
    # If the user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            color = request.POST.get('color')
            size = request.POST.get('size')
           

            

            try:
                variation = Variation.objects.get(product=product, color__iexact=color, size__iexact=size)
                product_variation.append(variation)


            except Variation.DoesNotExist:
                pass


        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing_variations -> database
            # current variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            print(ex_var_list)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()



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



def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    cart_item = CartItem.objects.filter(product=product, user=request.user)
    for item in cart_item:
             for variation in item.variations.all():
                 variation.quantity = max(0, variation.quantity + item.quantity)
                 variation.save()


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

       

                



            total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
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

        
       
        # i do this line just to see shipping value in temlate outside FOR LOOP
        total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
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


