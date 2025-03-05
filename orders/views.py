from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, OrderProduct
import json
from store.models import Product, Variation
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from marketing.models import Coupon, Promotion
from django.db import transaction 
from django.utils import timezone
from django.contrib import messages
from notification.models import Notification
from orders.models import State, City
from payment.models import AmountCheckout, Invoice, Payment
from analytics.models import OrderAnalytics

from django.contrib.auth.decorators import login_required
from affiliate.models import Affiliate
from carts.views import _cart_id
from django.contrib.auth.decorators import login_required
from carts.models import Cart
from django.contrib.auth.models import AnonymousUser
from django.db import transaction



def place_order(request, total=0, quantity=0):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        current_user = request.user
        # For authenticated users, get cart items associated with the user
        cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    else:
        # For anonymous users, use session to store and retrieve cart items
        cart_id = request.session.get('cart_id', None)
        if not cart_id:
            cart_id = _cart_id(request)

        cart = Cart.objects.get(cart_id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    
    # Check if there are any active items in the cart
    if not cart_items.exists():
        messages.error(request, "Your cart is empty. Add some items to place an order.")
        return redirect('store')

    grand_total = 0
    total_shipping_cost = 0
    discount_amount = 0
    promotion_discount = 0
    total = 0

    # Calculate the total amount of the cart items
    for cart_item in cart_items:
        sub_total = 0
        if cart_item.variations.exists():
            for variation in cart_item.variations.all():
                item_price = variation.clearance_price if variation.clearance_price > 0 else variation.price
                total += item_price * cart_item.quantity
        else:
            default_variation = cart_item.product.variations.first()
            if default_variation:
                item_price = default_variation.clearance_price if default_variation.clearance_price > 0 else default_variation.price
                total += item_price * cart_item.quantity

    # Determine shipping cost based on the shipping method
    shipping_method = request.POST.get('shipping_method', 'home')
    if len(cart_items) == 1:
        total_shipping_cost = sum(item.product.shipping for item in cart_items)
        if shipping_method == 'pickup':
            total_shipping_cost = total_shipping_cost / 2
    else:
        total_shipping_cost = 600  # Flat rate for multiple items

    # Apply promotion discount if available
    active_promotions = Promotion.objects.filter(
        is_active=True, 
        start_date__lte=timezone.now(), 
        end_date__gte=timezone.now()
    )
    for promotion in active_promotions:
        if promotion.is_valid() and cart_item.product.category in promotion.categories.all():
            promotion_discount += (item_price * cart_item.quantity) * (promotion.discount_percentage / 100)

    # Apply coupon discount if available
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.is_valid() and total >= coupon.minimum_purchase:
                discount_amount = coupon.discount_amount
            else:
                del request.session['coupon_code']
                messages.warning(request, "Coupon is invalid or does not meet minimum purchase requirements.")
        except Coupon.DoesNotExist:
            pass

    # Calculate grand total after discounts and shipping
    grand_total = total + total_shipping_cost - discount_amount - promotion_discount

    # Handle form submission for order placement
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create Order instance and populate details from form and calculated totals
                    order = Order()
                    order.user = current_user if request.user.is_authenticated else None  # If authenticated, assign user
                    order.is_guest = not request.user.is_authenticated  # Set is_guest to True if the user is anonymous
                    order.product = cart_item.product
                    order.first_name = form.cleaned_data['first_name']
                    order.last_name = form.cleaned_data['last_name']
                    order.phone = form.cleaned_data['phone']
                    order.address_line_1 = form.cleaned_data['address_line_1']
                    order.order_note = form.cleaned_data['order_note']
                    order.shipping_method = shipping_method
                    order.pickup_location = form.cleaned_data['pickup_location']
                    order.payment_method = form.cleaned_data['payment_method']
                    order.shipping_total = total_shipping_cost
                    order.order_total = grand_total
                    order.ip = request.META.get('REMOTE_ADDR')
                    #order.cart_id = cart.cart_id

                    # Get the state and city names and save them in the order
                    state = State.objects.get(id=form.cleaned_data['state'])
                    city = City.objects.get(id=form.cleaned_data['city'])
                    order.state = state.name  # Save state name
                    order.city = city.name  # Save city name
                    # Check if the order was placed through an affiliate link
                    affiliate_code = request.COOKIES.get('affiliate_code')
                    if affiliate_code:
                        try:
                            affiliate = Affiliate.objects.get(affiliate_code=affiliate_code)
                            order.purchased_through_affiliate = affiliate
                        except Affiliate.DoesNotExist:
                            pass  # Invalid affiliate code, ignore

                    
                    order.save()

                    # Generate unique order number
                    order.order_number = generate_order_number(order)
                    order.save()

                    # Create OrderProduct instances for each item in the cart
                    for cart_item in cart_items:
                        if cart_item.variations.exists():
                            for variation in cart_item.variations.all():
                                item_price = variation.clearance_price if variation.clearance_price > 0 else variation.price
                        else:
                            default_variation = cart_item.product.variations.first()
                            if default_variation:
                                item_price = default_variation.clearance_price if default_variation.clearance_price > 0 else default_variation.price

                        order_product = OrderProduct(
                            order=order,
                            user=current_user if request.user.is_authenticated else None,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            product_price=item_price,
                            ordered=False
                        )
                        order_product.save()

                        if cart_item.variations.exists():
                            order_product.variations.set(cart_item.variations.all())
                            order_product.save()
                        else:
                            # If the product has no variations, use the 'no_variant' variation
                            product_variation = cart_item.product.variations.filter(variant_type='no_variant').first()
                            if product_variation:
                                order_product.variations.set([product_variation])

                        order_product.save()

                # Pass order and calculated data to payment context
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'grand_total': grand_total,
                    'total_shipping_cost': total_shipping_cost,
                    'promotion_discount': promotion_discount,
                    'discount_amount': discount_amount,
                }
                return render(request, 'orders/payments.html', context)

            except Exception as e:
                print("Error while placing order: ", e)
                messages.error(request, "An error occurred while placing the order. Please try again.")
                return redirect('checkout')

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







from uuid import uuid4
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from analytics.models import OrderAnalytics
from payment.models import AmountCheckout, Invoice

from payment.services import PaymentService

def order_complete(request, order_number):
    total_shipping_cost = 0
    promotion_discount = 0
    coupon_discount = 0
    current_user = request.user if request.user.is_authenticated else None
    cart_items = []

    try:
        # Retrieve the order using the order number
        order = Order.objects.get(order_number=order_number)
       

       

        # Handle the case for anonymous users (use session for cart items)
        if current_user is None:
            cart_id = request.session.get('cart_id', None)
            if not cart_id:
                cart_id = _cart_id(request)  # Custom function for generating cart_id if not present
            cart = Cart.objects.get(cart_id=cart_id)
            cart_items = CartItem.objects.filter(cart=cart)
        else:
            # For authenticated users, get cart items associated with the user
            cart_items = CartItem.objects.filter(user=current_user)

        # Retrieve the associated OrderProducts
        ordered_products = OrderProduct.objects.filter(order=order)
        # Check if the ordered product is a digital product
        for ordered_product in ordered_products:
            if ordered_product.product.product_type == Product.DIGITAL:
                
                # Fetch previous paid orders by this user (exclude current order)
                previous_orders = Order.objects.filter(user=current_user, is_ordered=True).exclude(id=order.id).order_by('-id')

                
                # Loop through the previous orders to check for matching product names
                for prev_order in previous_orders:
                    prev_order_products = OrderProduct.objects.filter(order=prev_order)
                    
                    for prev_product in prev_order_products:
                        if prev_product.product.product_name == ordered_product.product.product_name:
                            # Check if the previous product's download is available (not expired and download count > 0)
                            print('Order:', prev_product.order.order_number)
                            # Add logging or print statements to check the values
                            print(f"Previous Product Download Expired: {prev_product.order.is_download_expired()}")
                            print(f"Previous Product Download Count: {prev_product.order.download_count}")

                            if prev_product.order.is_download_expired() or prev_product.order.download_count != 0:
                                # If the download is available, redirect to the download page
                                payment_service = PaymentService()
                                checkout_url = payment_service.create_checkout(order, order.payment_method, 'en')

                                return redirect(checkout_url)
                                
                            else:
                                # If the download has expired or download count is 0, proceed to checkout
                                return redirect('orders:download_purchase')
                           


        # Calculate subtotal for the products
        subtotal = sum(item.product_price * item.quantity for item in ordered_products)

        # Calculate total shipping cost
        num_cart_items = len(cart_items)
        if num_cart_items == 1:
            total_shipping_cost = sum(item.product.shipping for item in cart_items)
        else:
            total_shipping_cost = 600

        if order.shipping_method == 'pickup':
            total_shipping_cost = total_shipping_cost / 2  # Halve the shipping cost for pickup

        # Calculate promotion discount
        active_promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=now(),
            end_date__gte=now()
        )
        for item in ordered_products:
            for promotion in active_promotions:
                if promotion.is_valid() and item.product.category in promotion.categories.all():
                    promotion_discount += (item.product_price * item.quantity) * (promotion.discount_percentage / 100)

        # Calculate coupon discount if applied
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.is_valid() and subtotal >= coupon.minimum_purchase:
                    coupon_discount = coupon.discount_amount
                    coupon.save()
                    del request.session['coupon_code']
            except Coupon.DoesNotExist:
                pass

        # Calculate the grand total
        grand_total = subtotal + total_shipping_cost - promotion_discount - coupon_discount

        # Save the calculated values to the order
        order.subtotal = subtotal
        order.total_shipping_cost = total_shipping_cost
        order.promotion_discount = promotion_discount
        order.coupon_discount = coupon_discount
        order.save()

        # Handle 'cod' payment method
        if order.payment_method == 'cod':
            order.status = 'Completed'
            order.is_ordered = True
            order.save()

            for product in ordered_products:
                product.ordered = True
                product.save()

            CartItem.objects.filter(user=current_user).delete()  # For authenticated users
            # Analytics entry for 'cod'
            OrderAnalytics.objects.update_or_create(
                order_id=order,
                product_id=ordered_products[0].product.id,  # Associate the first product
                defaults={
                    'total_value': grand_total,
                    'quantity': sum(item.quantity for item in ordered_products),
                    'shipping_cost': total_shipping_cost,
                    'promotion_discount': promotion_discount,
                    'coupon_discount': coupon_discount,
                    'completed': True,
                    'user': current_user,
                    'created_at': now(),
                }
            )

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'total_shipping_cost': total_shipping_cost,
                'subtotal': subtotal,
                'promotion_discount': promotion_discount,
                'coupon_discount': coupon_discount,
                'grand_total': grand_total
            }
            return render(request, 'orders/order_complete.html', context)

        

        # Handle 'cib' or 'edahabia' payment methods
        if order.payment_method in ['cib', 'edahabia']:

            

           

            payment_service = PaymentService()
            try:
                # Call the payment service to get the checkout URL
                checkout_url = payment_service.create_checkout(order, order.payment_method, 'en')

                # Update the AmountCheckout with the checkout_url
                checkout = AmountCheckout.objects.get(entity_id=str(order.transaction_id))
                checkout.checkout_url = checkout_url
                checkout.save()

                # Create an invoice for the checkout
                Invoice.objects.create(
                    payment=checkout,
                    pdf=None  # Placeholder; add logic to generate the PDF if necessary
                )

                # Analytics entry for 'cib' or 'edahabia'
                OrderAnalytics.objects.update_or_create(
                    order_id=order,
                    product_id=ordered_products[0].product.id,  # Associate the first product
                    defaults={
                        'total_value': grand_total,
                        'quantity': sum(item.quantity for item in ordered_products),
                        'shipping_cost': total_shipping_cost,
                        'promotion_discount': promotion_discount,
                        'coupon_discount': coupon_discount,
                        'completed': False,  # Completed after successful payment
                        'user': current_user if request.user.is_authenticated else None,
                        'created_at': now(),
                    }
                )
                


                # Redirect to the checkout URL
                return redirect(checkout_url)
            except Exception as e:
                messages.error(request, f"Payment processing failed: {e}")
                return redirect('store')

        

        # Fallback context rendering if no specific handling
        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'total_shipping_cost': total_shipping_cost,
            'subtotal': subtotal,
            'promotion_discount': promotion_discount,
            'coupon_discount': coupon_discount,
            'grand_total': grand_total
        }
        return render(request, 'orders/order_complete.html', context)

    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect('store')


from datetime import timedelta

from django.utils import timezone

def payment_success(request, transaction_id):
    # Fetch the payment record using the transaction_id
    payment = get_object_or_404(AmountCheckout, entity_id=transaction_id)
    
    # Find the associated order
    order = get_object_or_404(Order, transaction_id=payment.entity_id)

    # Mark the payment as PAID and update the order status
    if payment.status != AmountCheckout.PAYMENT_STATUS.PAID:
        payment.on_paid()  # Mark payment as paid
        
        order.status = 'Paid'  # Update the order status
        order.is_ordered = True
        order.download_expiration = timezone.now() + timedelta(hours=24)  # Reset expiration
        order.download_count = 0  # Reset download count to 0 for the new order
        order.save()

        # Create an invoice if not already created
        invoice, created = Invoice.objects.get_or_create(
            payment=payment,
            defaults={'pdf': None}  # Placeholder for PDF generation logic
        )
        if created:
            messages.success(request, f"Invoice created for transaction ID: {transaction_id}")

    # Fetch the product associated with the order
    product = order.product

    # Prepare context for the template
    context = {
        'payment': payment,
        'order': order,
    }

    # If the order contains a digital product
    if product.product_type == Product.DIGITAL:
        context['digital_products'] = [product]  # Wrap in a list to maintain consistency
        context['download_links'] = [{
            'product_name': product.product_name,
            'download_url': f"/en/orders/digital_product/{product.slug}/download/"
        }]

    return render(request, 'orders/payment_success.html', context)


    



from datetime import timedelta
from django.utils import timezone
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.encoding import smart_str
import os

def download_product(request, product_slug):
    # Fetch the product by slug
    product = get_object_or_404(Product, slug=product_slug)
    
    # Check if the product is digital
    if product.product_type != Product.DIGITAL:
        return HttpResponseForbidden("This is not a digital product.")
    
    # Get the latest valid order for this product and user
    try:
        order = Order.objects.filter(
            product=product, user=request.user, status='Paid', is_ordered=True
        ).latest('created_at')  # Get the most recent order
    except Order.DoesNotExist:
        return HttpResponseForbidden("You do not have access to download this product.")

    # If this is a **new** purchase (new transaction ID), reset the expiration and download count
    if order.download_expiration is None or order.download_expiration < timezone.now():
        order.download_expiration = timezone.now() + timedelta(hours=24)  # Reset expiration for new order
        order.download_count = 0  # Reset download count for new order
        order.save()

    # Check if the download link has expired
    if order.is_download_expired():
        return HttpResponseForbidden("This download link has expired.")

    # Check if the user has exceeded the download limit
    if order.has_reached_download_limit():
        return HttpResponseForbidden("You have exceeded the number of allowed downloads.")
    
    # Increment the download count
    order.download_count += 1
    order.save()
    
    # Get the file path of the digital product
    digital_file_path = os.path.join(settings.MEDIA_ROOT, product.digital_file.name)

    # Check if the file exists
    if not os.path.exists(digital_file_path):
        return HttpResponseForbidden("The file is not available for download.")
    
    # Get the original filename and extension
    original_filename = os.path.basename(product.digital_file.name)  # Get the real filename with extension

    # Serve the file for download with the correct filename and extension
    with open(digital_file_path, 'rb') as file:
        response = HttpResponse(file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{smart_str(original_filename)}"'  # Serve the file with the real name
        return response







from django.shortcuts import render
from django.utils import timezone
from .models import Order, Product

def download_purchase(request):
    # Fetch the user's orders that are marked as 'Paid' and contain digital products
    orders = Order.objects.filter(user=request.user, status='Paid', is_ordered=True, is_download_removed=False).order_by('-id')

    # Initialize context to store download information
    download_links = []

    for order in orders:
        # Check if the product is digital
        if order.product.product_type == Product.DIGITAL:


            # Check if download expiration and limit are set
            if order.is_download_expired():
                download_status = "expired"
            elif order.has_reached_download_limit():
                download_status = "limit reached"
            else:
                download_status = "valid"

            # Calculate the remaining download attempts
            remaining_downloads = 3 - order.download_count 

            download_links.append({
                'order_id': order.id,
                'product_name': order.product.product_name,
                'order_number': order.order_number,
                'transaction_id': order.transaction_id,
                'image': order.product.images,
                'product_slug': order.product.slug,
                'download_url': f"/en/orders/digital_product/{order.product.slug}/download/",
                'download_status': download_status,
                'download_expiration': order.download_expiration,
                'download_count': order.download_count,
                'download_limit': 3,  # Or use any value that represents the download limit
                'remaining_downloads': remaining_downloads,
            })

    # Pass the list of download links to the template
    context = {
        'download_links': download_links,
        
    }

    return render(request, 'orders/download_purchase.html', context)


def remove_download(request, order_id):
    # Get the order by ID and ensure the user is the one who placed the order
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Mark the download as removed (hidden)
    order.is_download_removed = True
    order.save()

    # Redirect back to the download list page
    return redirect('orders:download_purchase')  # Redirect to your download list view


    


from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden, HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.contrib.auth.decorators import login_required
import pdfkit
import os
from django.utils.timezone import now

# Check if running on Heroku
if 'DYNO' in os.environ:
    WKHTMLTOPDF_CMD = '/app/bin/wkhtmltopdf'
else:
    WKHTMLTOPDF_CMD = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Local path
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)


def generate_invoice_pdf(order, context):
    """
    Generates a PDF for the given order and saves it to the filesystem.
    Returns the file path of the generated PDF.
    """
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'{order.transaction_id}_invoice.pdf')

    # Ensure the folder exists
    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

    # Load and render the template
    template = get_template('orders/invoice_pdf.html')
    html = template.render(context)

    # Generate the PDF
    pdfkit.from_string(html, pdf_file_path, configuration=pdfkit_config)

    return pdf_file_path




def view_invoice(request, transaction_id):
    order = get_object_or_404(Order, transaction_id=transaction_id)

    if order.user != request.user:
        return HttpResponseForbidden("You are not authorized to view this invoice.")

    order_products = order.orderproduct_set.all()

    

    # Prepare the context for rendering the PDF
    context = {
        'order': order,
        'order_products': order_products,
       
    }

    # Check if the PDF exists; if not, generate it
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'{order.transaction_id}_invoice.pdf')
    if not os.path.exists(pdf_file_path):
        pdf_file_path = generate_invoice_pdf(order, context)

    # Serve the PDF as an inline response
    try:
        pdf_file = open(pdf_file_path, 'rb')
        response = FileResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{transaction_id}.pdf"'
        return response
    except FileNotFoundError:
        return HttpResponse("Invoice PDF not found. Please try again later.", status=404)




def download_invoice(request, transaction_id):
    order = get_object_or_404(Order, transaction_id=transaction_id)

    if order.user != request.user:
        return HttpResponseForbidden("You are not authorized to download this invoice.")

    order_products = order.orderproduct_set.all()

    
    # Prepare the context for rendering the PDF
    context = {
        'order': order,
        'order_products': order_products,
        
    }

    # Check if the PDF exists; if not, generate it
    pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'{order.transaction_id}_invoice.pdf')
    if not os.path.exists(pdf_file_path):
        pdf_file_path = generate_invoice_pdf(order, context)

    # Serve the PDF as a downloadable response
    try:
        pdf_file = open(pdf_file_path, 'rb')
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{transaction_id}.pdf"'
        pdf_file.close()  # Close explicitly after response is sent
        return response
    except FileNotFoundError:
        return HttpResponse("Invoice PDF not found. Please try again later.", status=404)




from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from affiliate.models import AffiliateCommission

@receiver(post_save, sender=Order)
def create_affiliate_commission(sender, instance, created, **kwargs):
    print(f"Order created: {created}, Order ID: {instance.id}, User: {instance.user}")
    if created:
        try:
            print("Checking if user has a referred_by field and if the referred account has an affiliate.")
            # Check if the user has a referred_by field
            if hasattr(instance.user, 'referred_by') and instance.user.referred_by:
                print(f"User referred by: {instance.user.referred_by}")
                
                # Get the affiliate for the referred_by user (Account)
                referred_by_account = instance.user.referred_by
                affiliate = referred_by_account.affiliated  # This is the correct field
                commission_rate = instance.product.affiliate_percentage


                if affiliate:  # Ensure the referred user is an affiliate
                    commission_amount = instance.order_total * (commission_rate / 100)
                    print(f"Creating commission: {commission_amount} for affiliate: {affiliate}")
                    
                    # Create the affiliate commission entry
                    AffiliateCommission.objects.create(
                        affiliate=affiliate,
                        order=instance,
                        commission_amount=commission_amount
                    )

                    # Update total earnings of the affiliate
                    affiliate.total_earnings += commission_amount
                    affiliate.save()
                else:
                    print(f"Referred user {referred_by_account.email} is not an affiliate.")
        except Exception as e:
            print(f"Error creating affiliate commission: {e}")
