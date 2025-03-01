from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            # For authenticated users, get cart items based on the user
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                # For anonymous users, use the session cart_id to retrieve the cart
                cart = Cart.objects.filter(cart_id=_cart_id(request)).first()  # Ensure there's a cart for anonymous user
                cart_items = CartItem.objects.filter(cart=cart) if cart else []

            # Count the total quantity of items in the cart
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0
    return {'cart_count': cart_count}



from .models import Cart, CartItem
from .views import _cart_id

def Items(request):
    if request.user.is_authenticated:
        # For authenticated users, retrieve cart items based on the user
        cart_items = CartItem.objects.filter(user=request.user).prefetch_related('variations').order_by('-id')
        total_price = sum(item.sub_total() for item in cart_items)
    else:
        # For anonymous users, use session cart_id to retrieve the cart
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()  # Get cart for anonymous users
        cart_items = CartItem.objects.filter(cart=cart) if cart else []
        total_price = sum(item.sub_total() for item in cart_items)

    return {'item': cart_items, 'total_price': total_price}
