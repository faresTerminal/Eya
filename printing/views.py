from django.shortcuts import render, get_object_or_404
from orders.models import Order, OrderProduct
from django.template.loader import get_template
from django.http import HttpResponse
import pdfkit
from django.conf import settings
import os
from store.models import Product


# Create your views here.


def printing(request):
      current_user = request.user
      complete_orders = Order.objects.filter(product__buyer=current_user, status = 'Completed').order_by('-id')
      context = {
	'complete_orders': complete_orders,
	} 
      return render(request, 'printing/printing.html', context)

def order_detail(request, order_id):
   
    order = get_object_or_404(Order, id=order_id)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)

    subtotal = 0
    for i in ordered_products:
        subtotal += i.product_price * i.quantity
    # Calculate total shipping cost for ordered products
    total_shipping_cost = sum(item.product.shipping for item in ordered_products)

    
    context = {
    'order': order,
    'ordered_products': ordered_products,
    'subtotal': subtotal,
    'total_shipping_cost': total_shipping_cost,
    'ordered_products': ordered_products,
    
    }
    return render(request, 'printing/order_detail.html', context)






# Define pdfkit_config with the path to wkhtmltopdf
WKHTMLTOPDF_CMD = ''
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

def generate_and_save_pdf(request, order_id):
    try:
        # Retrieve the order and ordered products based on the order_id
        order = Order.objects.get(id=order_id)
        ordered_products = OrderProduct.objects.filter(order_id=order_id)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
        # Calculate total shipping cost for ordered products
        total_shipping_cost = sum(item.product.shipping for item in ordered_products)

        # Load your order detail template and render it
        template = get_template('printing/order_detail.html')
        context = {
            'order': order,
            'subtotal': subtotal,
            'total_shipping_cost': total_shipping_cost,
            'ordered_products': ordered_products,
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
        response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf'
        with open(pdf_file, 'rb') as pdf_content:
            response.write(pdf_content.read())

        return response
    except Order.DoesNotExist:
        # Handle the case where the order with the provided ID does not exist
        return HttpResponse("Order not found", status=404)
