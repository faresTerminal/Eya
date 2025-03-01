from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation, Coupon
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from store.forms import CouponForm
from django.utils import timezone
# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from marketing.models import Coupon, Promotion, CouponUsage
from orders.models import State, City


def _cart_id(request):
    # Generate a cart_id using session key or create a new session if none exists
    cart_id = request.session.session_key
    print("Session Key: ", cart_id)  # Debugging line to check the session key
    
    if not cart_id:
        request.session.create()  # This will create a session key if it doesn't exist
        cart_id = request.session.session_key

    # Ensure the session key is saved in the Cart model when no cart exists
    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        cart = Cart(cart_id=cart_id)
        cart.save()  # Save the cart to the database with the session key

    return cart_id




 
def _get_or_create_variations(product, color, size):
    """
    Helper function to fetch variations based on color and size, or return None if no variations.
    """
    product_variation = []
    variation_id = None

    # If both color and size are provided
    if color and size:
        # Filter by color's name and size field in Variation
        variations = Variation.objects.filter(
            product=product, 
            color__name__iexact=color,  # Access color's name field
            size__iexact=size           # Directly use size (CharField)
        )
        if variations.exists():
            product_variation = list(variations)  # Append all matching variations
            variation_id = variations.first().id  # Use the first variation's ID
    # If only color is provided
    elif color:
        variations = Variation.objects.filter(
            product=product, 
            color__name__iexact=color  # Access color's name field
        )
        if variations.exists():
            product_variation = list(variations)
            variation_id = variations.first().id
    # If only size is provided
    elif size:
        variations = Variation.objects.filter(
            product=product, 
            size__iexact=size  # Directly use size (CharField)
        )
        if variations.exists():
            product_variation = list(variations)
            variation_id = variations.first().id

    return product_variation, variation_id





   
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # Get the product

    # Check if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []  # Initialize variations list
        variation_id = None  # Initialize variation_id

        # Check if product has variations (color/size)
        if product.variations.exists():
            color = request.POST.get('color')  # Get color from POST request
            size = request.POST.get('size')  # Get size from POST request

            try:
                # Get or create variations (returns a list of variations and the variation ID)
                product_variation, variation_id = _get_or_create_variations(product, color, size)
            except Variation.DoesNotExist:
                pass  # Handle case where the variation does not exist

            # Check if the cart item already exists for the specific variation
            is_cart_item_exists = CartItem.objects.filter(
                product=product, 
                user=current_user, 
                variations__in=product_variation if product_variation else [],
                variation_id=variation_id
            ).exists()

        else:
            # If no variants exist, treat the product as a simple item (without variations)
            is_cart_item_exists = CartItem.objects.filter(
                product=product, 
                user=current_user, 
                variations=None
            ).exists()

        quantity = int(request.POST.get('quantity', 1))  # Get the quantity from the POST request (default is 1)

        if is_cart_item_exists:
            # If the cart item exists, increase the quantity
            cart_item = CartItem.objects.get(
                product=product, 
                user=current_user, 
                variation_id=variation_id
            )
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # If the cart item does not exist, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                user=current_user,
                variation_id=variation_id
            )
            if product_variation:
                cart_item.variations.add(*product_variation)  # Add variations to the cart item

            cart_item.save()

        # Update variation quantities (only if there are variations)
        for variation in cart_item.variations.all():
            variation.quantity = max(0, variation.quantity - cart_item.quantity)  # Decrease quantity
            variation.save()

    else:
        # Handle cart addition for anonymous users (using session-based cart)
        color = request.POST.get('color')  # Get color from POST request
        size = request.POST.get('size')  # Get size from POST request

        # Get or create variations (returns variations list and variation_id)
        product_variation, variation_id = _get_or_create_variations(product, color, size)

        # Get or create the session-based cart
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # Get cart using session key
        except Cart.DoesNotExist:
            # If no cart exists, create a new one for the session
            cart = Cart.objects.create(cart_id=_cart_id(request))
        
        if product.variations.exists():
            # If product has variants, check if the item exists in the cart
            is_cart_item_exists = CartItem.objects.filter(
                product=product, 
                cart=cart, 
                variations__in=product_variation if product_variation else [],
                variation_id=variation_id
            ).exists()
        else:
            # If no variants exist, check for cart item without variations
            is_cart_item_exists = CartItem.objects.filter(
                product=product, 
                cart=cart, 
                variations=None
            ).exists()

        quantity = int(request.POST.get('quantity', 1))  # Get the quantity from the POST request (default is 1)

        if is_cart_item_exists:
            # If the cart item exists, increase the quantity
            cart_item = CartItem.objects.get(
                product=product, 
                cart=cart, 
                variation_id=variation_id
            )
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # If the cart item does not exist, create a new one
            cart_item = CartItem.objects.create(
                product=product,
                quantity=quantity,
                cart=cart,  # Associate the cart with the session-based cart
                variation_id=variation_id
            )
            if product_variation:
                cart_item.variations.add(*product_variation)  # Add variations to the cart item

            cart_item.save()

        # Update variation quantities (only if there are variations)
        for variation in cart_item.variations.all():
            variation.quantity = max(0, variation.quantity - cart_item.quantity)  # Decrease quantity
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





def remove_cart_item(request, product_id, cart_item_id, variation_id=None):
    # Retrieve the product
    product = get_object_or_404(Product, id=product_id)

    # Get the cart item (based on whether the user is authenticated or not)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)

    # If a variation_id is provided, handle removing the variation
    if variation_id:
        # Find the specific variation within the cart item
        variation = cart_item.variations.get(id=variation_id)

        # Adjust the variation quantity (if needed)
        variation.quantity = max(0, variation.quantity + cart_item.quantity)
        variation.save()

        # Remove the variation from the cart item
        cart_item.variations.remove(variation)

        # If there are no more variations in the cart item, delete the cart item
        if cart_item.variations.count() == 0:
            cart_item.delete()
    else:
        # If no variation_id is passed, simply delete the cart item
        cart_item.delete()

    # Check if the cart is now empty after removing the item
    remaining_cart_items = CartItem.objects.filter(
        user=request.user if request.user.is_authenticated else None,
        cart=Cart.objects.get(cart_id=_cart_id(request)) if not request.user.is_authenticated else None,
        is_active=True
    )

    # If the cart is empty and a coupon was applied, reduce coupon usage count and remove CouponUsage
    coupon_code = request.session.get('coupon_code')
    if remaining_cart_items.count() == 0 and coupon_code:
        try:
            # Get the coupon that was applied
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            
            # Check if the coupon has been used and decrement its usage count
            if coupon.used_count > 0:
                coupon.used_count -= 1
                coupon.save()

            # Remove the CouponUsage record for this user and coupon
            if request.user.is_authenticated:
                CouponUsage.objects.filter(coupon=coupon, user=request.user).delete()

            # Remove the coupon from the session
            del request.session['coupon_code']

        except Coupon.DoesNotExist:
            pass

    return redirect('cart')

def calculate_totals(cart_items, coupon_code):
    """Helper function to calculate total and discount."""
    total = quantity = 0
    discount_amount = 0
    
    for cart_item in cart_items:
        # Check if the cart item has variations
        if cart_item.variations.exists():
            # If variations exist, iterate through all variations for the item
            for variation in cart_item.variations.all():
                # Use clearance_price if it exists and is greater than 0, otherwise fallback to price
                price = variation.clearance_price if variation.clearance_price > 0 else variation.price
                
                # Add the calculated price for the variation multiplied by quantity to the total
                total += price * cart_item.quantity
                quantity += cart_item.quantity
        else:
            # If no variations exist, treat the product as having a single variation
            # You can create a "dummy" variation for such products if needed or use the default behavior.
            # Here, we treat the product as having one variation, which is the base variation.
            # We fetch the first variation (there should always be at least one variation for "simple" products).
            
            default_variation = cart_item.product.variations.first()
            if default_variation:
                price = default_variation.clearance_price if default_variation.clearance_price > 0 else default_variation.price
                total += price * cart_item.quantity
                quantity += cart_item.quantity

    # Apply coupon discount if applicable
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_valid() and total >= coupon.minimum_purchase:
                discount_amount = coupon.discount_amount
        except Coupon.DoesNotExist:
            pass  # Ignore invalid or expired coupons

    return total, quantity, discount_amount






def cart(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # For authenticated users, filter by user
        cart_items = CartItem.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-id')
    else:
        # For anonymous users, get or create a session-based cart
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(
                cart=cart,
                is_active=True
            ).order_by('-id')
        except Cart.DoesNotExist:
            # If the cart doesn't exist, create a new one for the session
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart_items = []

    # Get the coupon code from session
    coupon_code = request.session.get('coupon_code')
    
    # Calculate totals for the cart items
    total, quantity, discount_amount = calculate_totals(cart_items, coupon_code)

    # Calculate the total shipping cost
    if len(cart_items) == 1:
        total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
    else:
        total_shipping_cost = 600  # Default shipping cost for multiple items

    # Calculate the grand total
    grand_total = total + total_shipping_cost - discount_amount

    # Calculate sub_total for each cart item
    for cart_item in cart_items:
        sub_total = 0
        # If the cart item has variations
        if cart_item.variations.exists():
            for variation in cart_item.variations.all():
                # Use clearance_price if available, otherwise fallback to regular price
                price = variation.clearance_price if variation.clearance_price > 0 else variation.price
                sub_total += price * cart_item.quantity
        else:
            # If no variations, use the product's default variation
            default_variation = cart_item.product.variations.first()
            if default_variation:
                price = default_variation.clearance_price if default_variation.clearance_price > 0 else default_variation.price
                sub_total += price * cart_item.quantity

        # Set the sub_total for the cart item
        cart_item.sub_total = sub_total

    # Prepare context data for rendering
    context = {
        'total': total,
        'quantity': quantity,
        'total_shipping_cost': total_shipping_cost,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'discount_amount': discount_amount,
        'coupon_code': coupon_code,
    }

    return render(request, 'store/cart.html', context)







def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        grand_total = 0
        total_shipping_cost = 0  # Initialize total_shipping_cost to avoid unbound variable error
        discount_amount = 0  # Initialize discount amount for coupon
        promotion_discount = 0  # Discount from promotions
        
        # Get cart items for authenticated users or anonymous users
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Initialize an empty list to store sub_totals for each item
        for cart_item in cart_items:
            sub_total = 0  # Initialize the sub_total for each cart_item

            # If cart_item has variations, calculate the sub_total based on variations
            if cart_item.variations.exists():
                for variation in cart_item.variations.all():
                    # Use clearance_price if available and greater than 0, otherwise fallback to regular price
                    price = variation.clearance_price if variation.clearance_price > 0 else variation.price
                    sub_total += price * cart_item.quantity
            else:
                # If no variations, calculate the sub_total based on the product's default variation
                default_variation = cart_item.product.variations.first()
                if default_variation:
                    price = default_variation.clearance_price if default_variation.clearance_price > 0 else default_variation.price
                    sub_total += price * cart_item.quantity

            # Add the sub_total to the total for this cart_item
            cart_item.sub_total = sub_total
            total += sub_total  # Add the sub_total to the grand total
            quantity += cart_item.quantity  # Add the quantity of the cart_item to the total quantity

            # Apply promotions (if any)
            product = cart_item.product
            variation = cart_item.variations.first()
            if variation:
                active_promotions = Promotion.objects.filter(
                    is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now()
                )
                
                for promotion in active_promotions:
                    # Apply discount if promotion is valid for the product's category
                    if promotion.is_valid() and product.category in promotion.categories.all():
                        promotion_discount += (variation.price * cart_item.quantity) * (promotion.discount_percentage / 100)

        # Calculate shipping cost based on the number of cart items
        num_cart_items = len(cart_items)
        if num_cart_items == 1:
            total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
        else:
            total_shipping_cost = 600  # Set total_shipping_cost to 600 DA for more than one item

        # Apply coupon discount if a valid coupon is available
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid():
                    discount_amount = coupon.discount_amount
            except Coupon.DoesNotExist:
                pass

        # Calculate grand total with discounts
        grand_total = total + total_shipping_cost - discount_amount - promotion_discount

        states = State.objects.all()

       


    except ObjectDoesNotExist:
        pass  # Just ignore

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'total_shipping_cost': total_shipping_cost,
        'discount_amount': discount_amount,
        'promotion_discount': promotion_discount,
        'grand_total': grand_total,
        'states': states,
    }

    return render(request, 'store/checkout.html', context)


def increment_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.quantity += 1
    cart_item.save()
    
    messages.success(request, "Item quantity updated successfully!")
    return redirect('cart')