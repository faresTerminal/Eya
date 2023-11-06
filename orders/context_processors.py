# context_processors.py

from .models import Order, Product

def seller_order_count(request):
    # Check if the user is logged in and is a seller
    if request.user.is_authenticated:
        # Count the number of orders for the seller's products
        seller_order_count = Order.objects.filter(product__buyer=request.user, status = 'Completed').count()
    else:
        seller_order_count = 0  # Default value for non-sellers
    
    # Return the seller order count as a context variable
    return {'seller_order_count': seller_order_count}

