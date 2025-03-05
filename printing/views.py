from django.shortcuts import render, get_object_or_404
from orders.models import Order, OrderProduct
from django.template.loader import get_template
from django.http import HttpResponse
import pdfkit
from django.conf import settings
import os
from store.models import Product
from marketing.models import Promotion, Coupon
from django.utils import timezone


# Create your views here.




from decimal import Decimal

def order_detail(request, order_id):
    # Retrieve the order and its products
    order = get_object_or_404(Order, id=order_id)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)

    # Calculate subtotal
    subtotal = sum(item.product_price * item.quantity for item in ordered_products)

    # Calculate total shipping cost
    num_cart_items = len(ordered_products)
    total_shipping_cost = 600 if num_cart_items > 1 else sum(item.product.shipping for item in ordered_products)

    # Adjust shipping cost for "pickup" method
    if order.shipping_method == 'pickup':
        total_shipping_cost = total_shipping_cost / 2  # Halve shipping cost for pickup

    # Get active promotions
    active_promotions = Promotion.objects.filter(
        is_active=True, 
        start_date__lte=timezone.now(), 
        end_date__gte=timezone.now()
    )

    # Initialize discounts
    coupon_discount = 0
    promotion_discount = 0

    # Calculate coupon discount if applied
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            if coupon.expiration_date >= timezone.now() and (coupon.minimum_purchase is None or subtotal >= coupon.minimum_purchase):
                coupon_discount = coupon.discount_amount
        except Coupon.DoesNotExist:
            coupon_discount = 0  # If the coupon is invalid, keep discount at 0

    # Calculate promotion discounts
    for item in ordered_products:
        for promotion in active_promotions:
            if promotion.is_valid() and item.product.category in promotion.categories.all():
                promotion_discount += (item.product_price * item.quantity) * (promotion.discount_percentage / 100)

    # Calculate grand total
    grand_total = subtotal + total_shipping_cost - coupon_discount - promotion_discount

    # Prepare context for rendering
    context = {
        'order': order,
        'ordered_products': ordered_products,
        'subtotal': subtotal,
        'total_shipping_cost': total_shipping_cost,
        'active_promotions': active_promotions,
        'coupon_discount': coupon_discount,
        'promotion_discount': promotion_discount,
        'grand_total': grand_total,
    }

    return render(request, 'printing/order_detail.html', context)








# Check if running on Heroku
if 'DYNO' in os.environ:
    WKHTMLTOPDF_CMD = '/app/bin/wkhtmltopdf'
else:
    WKHTMLTOPDF_CMD = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Local path

pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

def generate_and_save_pdf(request, order_id):
    try:
        # Retrieve the order and ordered products based on the order_id
        order = get_object_or_404(Order, id=order_id)
        ordered_products = OrderProduct.objects.filter(order_id=order_id)

        # Calculate subtotal
        subtotal = sum(item.product_price * item.quantity for item in ordered_products)

        # Calculate total shipping cost
        num_cart_items = len(ordered_products)
        total_shipping_cost = 600 if num_cart_items > 1 else sum(item.product.shipping for item in ordered_products)

        # Adjust shipping cost for "pickup" method
        if order.shipping_method == 'pickup':
            total_shipping_cost = total_shipping_cost / Decimal(2)  # Halve shipping cost for pickup

        # Initialize discounts
        coupon_discount = 0
        promotion_discount = 0

        # Get active promotions
        active_promotions = Promotion.objects.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )

        # Calculate coupon discount if applied
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.expiration_date >= timezone.now() and (coupon.minimum_purchase is None or subtotal >= coupon.minimum_purchase):
                    coupon_discount = coupon.discount_amount
            except Coupon.DoesNotExist:
                coupon_discount = 0

        # Calculate promotion discount
        if active_promotions.exists():
            # Assuming you want to apply the first valid promotion found
            for promotion in active_promotions:
                if promotion.discount_percentage > 0 and subtotal >= 0:
                    promotion_discount += (subtotal * promotion.discount_percentage) / 100
                    break  # Remove this line if you want to apply multiple promotions

        # Calculate grand total
        grand_total = subtotal + total_shipping_cost - coupon_discount - promotion_discount

        # Load your order detail template and render it
        template = get_template('printing/order_detail.html')
        context = {
            'order': order,
            'subtotal': subtotal,
            'total_shipping_cost': total_shipping_cost,
            'ordered_products': ordered_products,
            'coupon_discount': coupon_discount,
            'promotion_discount': promotion_discount,
            'grand_total': grand_total,
        }
        html = template.render(context)

        # Specify the folder path on the desktop
        desktop_folder = os.path.expanduser("~/Desktop")
        order_list_folder = os.path.join(desktop_folder, "orderList")

        # Create the "orderList" folder if it doesn't exist
        if not os.path.exists(order_list_folder):
            os.makedirs(order_list_folder)

        # Construct the PDF file path within the "orderList" folder
        pdf_file = os.path.join(order_list_folder, f'order_{order_id}.pdf')

        # Define pdfkit options to disable external links
        pdfkit_options = {
            'disable-external-links': True,
        }

        # Generate PDF from HTML using pdfkit with options
        pdfkit.from_string(html, pdf_file, configuration=pdfkit_config, options=pdfkit_options)

        # Return the PDF file as an HttpResponse for immediate download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'
        with open(pdf_file, 'rb') as pdf_content:
            response.write(pdf_content.read())

        return response
    except Order.DoesNotExist:
        # Handle the case where the order with the provided ID does not exist
        return HttpResponse("Order not found", status=404)