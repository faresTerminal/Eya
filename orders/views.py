from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.db import transaction 




def place_order(request, total = 0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    

    for cart_item in cart_items:
        if cart_item.product.clearance_price:
            total += (cart_item.product.clearance_price * cart_item.quantity)
        else:
            total += (cart_item.product.price * cart_item.quantity)

    
    grand_total += total 

    

    total_shipping_cost = sum(cart_item.product.shipping for cart_item in cart_items)
    grand_total += total_shipping_cost

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Use a database transaction to ensure data consistency
            with transaction.atomic():
                # Create the Order object
                order = Order()
                order.user = current_user
                order.product = cart_item.product
                order.first_name = form.cleaned_data['first_name']
                order.last_name = form.cleaned_data['last_name']
                order.phone = form.cleaned_data['phone']
                order.address_line_1 = form.cleaned_data['address_line_1']
                order.state = form.cleaned_data['state']
                order.city = form.cleaned_data['city']
                order.order_note = form.cleaned_data['order_note']
                order.shipping_total = total_shipping_cost
                order.order_total = grand_total
                order.ip = request.META.get('REMOTE_ADDR')
                order.save()

                # Generate order number and update the order
                order_number = generate_order_number(order)
                order.order_number = order_number
                order.save()

                # Create and save OrderProduct objects
                for cart_item in cart_items:
                    orderproduct = OrderProduct()
                    orderproduct.order = order
                    orderproduct.user = current_user
                    orderproduct.product = cart_item.product
                    orderproduct.quantity = cart_item.quantity

                    if cart_item.product.clearance_price:
                        orderproduct.product_price = cart_item.product.clearance_price
                    else:
                        orderproduct.product_price = cart_item.product.price

                    orderproduct.ordered = True
                    orderproduct.save()

                    

                    cart_item = CartItem.objects.get(id=cart_item.id)
                    product_variation = cart_item.variations.all()
                    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                    orderproduct.variations.set(product_variation)
                    orderproduct.save()

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'grand_total': grand_total,
                
                'total_shipping_cost': total_shipping_cost,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def generate_order_number(order):
    # Generate an order number based on your criteria
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr, mt, dt)
    current_date = d.strftime("%Y%m%d")  # 20210305
    return current_date + str(order.id)


def order_complete(request, order_number):
    current_user = request.user
    try:
        order = Order.objects.get(order_number=order_number)
        order.status = 'Completed'
        order.is_ordered = True
        order.save()
        
        # Retrieve the associated OrderProducts and mark them as ordered
        ordered_products = OrderProduct.objects.filter(order=order)
        for product in ordered_products:
            product.ordered = True
            product.save()

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        cart_items = CartItem.objects.filter(user=current_user)
        for item in cart_items:
          total_shipping_cost = sum(item.product.shipping for item in cart_items)


        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

        

        # Clear cart
        CartItem.objects.filter(user=request.user).delete()


        # Send order recieved email to customer
        '''
        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_recieved_email.html', {
          'user': request.user,
          'order': order,
        })
        to_email = order.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        '''

        
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'total_shipping_cost': total_shipping_cost,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except Order.DoesNotExist:
        # Handle the case where the order with the provided order_number doesn't exist.
        # You might want to show an error page or redirect to another page.
        return redirect('store')  # Redirect to the store or an error page





"""
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
"""