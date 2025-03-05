from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Payment, SubscriptionPlan, Invoice, AmountCheckout
from accounts.models import Account
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.utils.timezone import now  # Import 'now' for current time
from datetime import timedelta
from django.utils import timezone
import pdfkit
from django.template.loader import get_template
import os
from django.conf import settings
from orders.models import Order, OrderProduct
# Subscription Plan Views
def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)  # Only active plans will be displayed
    return render(request, 'payment/subscription_plans.html', {'plans': plans})


import random
import string

def generate_transaction_id(user, plan):
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"TXN-{user.id}-{plan.id}-{random_string}"

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Payment, Invoice
from accounts.models import Account

from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from .models import SubscriptionPlan, Payment, Invoice
from .services import SubscriptionService
import uuid
from datetime import timedelta

def subscribe_to_plan(request, plan_id):
    """
    Handle user subscription to a plan.
    """
    user = request.user  # Get the currently logged-in user
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)  # Retrieve the subscription plan

    # Step 1: Check if the user has an active subscription or trial
    subscription_status_response = SubscriptionService.check_user_subscription_status(user)
    if subscription_status_response:
        return subscription_status_response  # If the user has an active subscription, return the response

    # Step 2: Create the checkout session and get the checkout URL
    payment_method = request.POST.get('gateway', 'CHARGILY')  # Default to 'CHARGILY' if not specified
    locale = request.LANGUAGE_CODE  # Get the user's preferred language

    try:
        # Use the SubscriptionService to create the checkout session
        checkout = SubscriptionService.create_checkout(user, plan, payment_method, locale)
        print(f"Checkout Created: Entity ID {checkout.entity_id}, URL {checkout.checkout_url}")

        # Step 4: Create an invoice for the payment
        invoice = SubscriptionService.create_invoice(checkout)
        print(f"Invoice Created for Payment ID: {checkout.id}")

        # Step 5: Redirect the user to the Chargily checkout page
        return redirect(checkout.checkout_url)

    except Exception as e:
        print(f"Error during subscription process: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response: {e.response.status_code} - {e.response.text}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


from affiliate.models import Affiliate, AffiliateCommission
from orders.models import Order
from .services import AffiliatePaymentService



def pay_affiliate_commission(request, commission_id):
    """
    Handle the payment of affiliate commission.
    The buyer of the product pays the affiliate's commission.
    """
    # Get the affiliate commission object
    affiliate_commission = get_object_or_404(AffiliateCommission, id=commission_id)

    # Ensure that the commission has not already been paid
    if affiliate_commission.is_paid:
        return HttpResponse("The commission has already been paid.", status=400)

    # Get the order associated with the commission
    order = affiliate_commission.order
    affiliate = affiliate_commission.affiliate

    # Check if the buyer is the one making the payment (the user who placed the order)
    if order.product.buyer != request.user:
        return HttpResponse("You are not authorized to pay for this affiliate commission.", status=403)

    # Step 1: Check if the buyer has an active subscription (or is a valid customer)
    subscription_status_response = AffiliatePaymentService.check_buyer_subscription_status(request.user)
    if subscription_status_response:
        return subscription_status_response  # If the buyer is not valid, return the response

    # Step 2: Create the checkout session and get the checkout URL
    payment_method = request.POST.get('gateway', 'CHARGILY')  # Default to 'CHARGILY' if not specified
    locale = request.LANGUAGE_CODE  # Get the user's preferred language

    try:
        # Step 3: Create a checkout session for the affiliate payment
        checkout_url = AffiliatePaymentService.create_checkout_for_affiliate_payment(
            request.user, affiliate_commission, payment_method, locale)

        # Step 4: Redirect the user to the Chargily checkout page
        return redirect(checkout_url)

    except Exception as e:
        print(f"Error during affiliate payment process: {str(e)}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)



def pay_all_pending_affiliate_commissions(request, affiliate_id):
    """
    Handle the payment of all pending affiliate commissions for a specific affiliate.
    """
    # Get the affiliate object
    affiliate = get_object_or_404(Affiliate, id=affiliate_id)

    # Get all pending commissions for the affiliate
    pending_commissions = AffiliateCommission.objects.filter(affiliate=affiliate, is_paid=False)

    if not pending_commissions:
        return HttpResponse("No pending commissions to pay.", status=404)

    # Step 1: Check if the buyer has an active subscription (or is a valid customer)
    subscription_status_response = AffiliatePaymentService.check_buyer_subscription_status(request.user)
    if subscription_status_response:
        return subscription_status_response  # If the buyer is not valid, return the response

    # Step 2: Create the checkout session and get the checkout URL
    payment_method = request.POST.get('gateway', 'CHARGILY')  # Default to 'CHARGILY' if not specified
    locale = request.LANGUAGE_CODE  # Get the user's preferred language

    # Collect the total commission amount to be paid (sum of all pending commissions)
    total_amount = sum(commission.commission_amount for commission in pending_commissions)

    try:
        # Step 3: Create a checkout session for the total amount (all pending commissions)
        checkout_url = AffiliatePaymentService.create_checkout_for_affiliate_payment(
            request.user, pending_commissions, payment_method, locale, total_amount  # Pass the total amount
        )

        # Step 4: Redirect the user to the checkout page
        return redirect(checkout_url)

    except Exception as e:
        print(f"Error during affiliate payment process: {str(e)}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)






def failure(request):
    return render(request, 'payment/payment_error.html')

def subscription_success(request, transaction_id):
    payment = get_object_or_404(AmountCheckout, entity_id=transaction_id)
    return render(request, 'payment/subscription_success.html', {'payment': payment})

def subscription_needed(request):
    # Fetch all active subscription plans
    active_plans = SubscriptionPlan.objects.filter(is_active=True)

    # Pass the plans to the template

    return render(request, 'payment/subscription_needed.html', {'plans': active_plans})



def trial_expired(request):
    return render(request, 'payment/trial_expired.html')

def check_active_subscription(request):
      # Adjust the filter logic as needed
    
    return render(request, 'payment/sub_is_active.html')


@login_required
def payment_status(request):
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    return render(request, 'payment/payment_status.html', {'payments': payments})

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponseForbidden
from .models import Invoice
from django.contrib.auth.decorators import login_required

# Check if running on Heroku
if 'DYNO' in os.environ:
    WKHTMLTOPDF_CMD = '/app/bin/wkhtmltopdf'
else:
    WKHTMLTOPDF_CMD = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Local path
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_CMD)

@login_required
def view_invoice(request, transaction_id):
    # Fetch the invoice based on the transaction_id
    invoice = get_object_or_404(Invoice, payment__entity_id=transaction_id)

    # Ensure the logged-in user is authorized to view this invoice
    if invoice.payment.customer != request.user:
        return HttpResponseForbidden("You are not authorized to view this invoice.")

     # If the PDF exists, serve it as a downloadable response
    if invoice.pdf:
        # Access the actual file path using the `.path` attribute of FieldFile
        file_path = invoice.pdf.path  # This is the actual file path
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{transaction_id}.pdf"'
        return response

    # Check if the PDF file exists for this invoice
    if not invoice.pdf:
        # If not, generate and save the PDF dynamically
        # Load the template for the invoice
        template = get_template('payment/invoice_pdf.html')
        context = {
            'invoice': invoice,
            'payment': invoice.payment,
            'user': invoice.payment.customer,
        }

        # Render the HTML content
        html = template.render(context)

        # Define the path to save the PDF
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'{invoice.payment.entity_id}_invoice.pdf')

        # Ensure the folder exists
        os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

        # Generate the PDF and save it
        pdfkit.from_string(html, pdf_file_path, configuration=pdfkit_config)

        # Save the PDF path to the invoice model
        invoice.pdf = pdf_file_path
        invoice.save()

   

    # If no PDF exists after generation attempt, show invoice details
    return render(request, 'payment/view_invoice.html', {'invoice': invoice})






def download_invoice(request, transaction_id):
    try:
        # Get the invoice by transaction_id
        invoice = get_object_or_404(Invoice, payment__entity_id=transaction_id)

        # Load the invoice template to render the PDF content
        template = get_template('payment/invoice_pdf.html')
        context = {
            'invoice': invoice,
            'payment': invoice.payment,
            'user': invoice.payment.customer,
        }

        html = template.render(context)

        # Generate the PDF from the rendered HTML
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f'{invoice.payment.entity_id}_invoice.pdf')

        # Ensure the directory exists
        os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)

        # Generate the PDF using pdfkit and save it to the file system
        pdfkit.from_string(html, pdf_file_path, configuration=pdfkit_config)

        # Return the PDF file as an HttpResponse for immediate download
        with open(pdf_file_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{invoice.payment.entity_id}_invoice.pdf"'
            return response

    except Invoice.DoesNotExist:
        return HttpResponse("Invoice not found", status=404)

# Checkout Views
def checkout(request, amount_checkout_id):
    checkout = get_object_or_404(AmountCheckout, id=amount_checkout_id)
    return render(request, 'payment/checkout.html', {'checkout': checkout})


from affiliate.models import AffiliateCommission





# views.py

import hashlib
import hmac
import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging
from carts.models import CartItem
from decimal import Decimal
 # Import your models

# Replace this with your actual Chargily API secret key
API_SECRET_KEY = 'test_sk_hte7uSRfuRtDFHpL0T23zOGMAY3zjcqQbY590tkD'

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def webhook(request):
    try:
        payload = request.body.decode('utf-8')
        signature = request.headers.get('signature')

        if not signature or not payload:
            return HttpResponse("Missing signature or payload", status=400)

        computed_signature = hmac.new(
            API_SECRET_KEY.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, computed_signature):
            return HttpResponse("Invalid signature", status=403)

        event = json.loads(payload)
        event_type = event.get('type')
        checkout_data = event.get('data')

        if not checkout_data or 'id' not in checkout_data:
            return HttpResponse("Invalid payload structure", status=400)

        amount_checkout_id = checkout_data['id']

        try:
            amount_checkout = AmountCheckout.objects.get(checkout_url__icontains=amount_checkout_id)
            if event_type == 'checkout.paid':
                # Mark payment as paid
                amount_checkout.on_paid()

                # Check and update affiliate commission payment status
                affiliate_commission = AffiliateCommission.objects.filter(commission_amount=Decimal(str(amount_checkout.amount))).first()
                if affiliate_commission:
                    affiliate_commission.is_paid = True

                    affiliate_commission.payment_reference = checkout_data.get('reference')  # Set payment reference if available
                    affiliate_commission.save()
                    logger.info(f"Affiliate commission for {affiliate_commission.affiliate.user.email} marked as paid.")

                # Activate subscription for the associated user
                user = amount_checkout.customer
                if user:
                    subscription_plan = amount_checkout.plan
                    if subscription_plan:
                        from datetime import timedelta
                        from django.utils.timezone import now

                        current_date = now()
                        if user.subscription_active and user.subscription_expiry_date and user.subscription_expiry_date > current_date:
                            user.subscription_expiry_date += timedelta(days=subscription_plan.duration_days)
                        else:
                            user.subscription_expiry_date = current_date + timedelta(days=subscription_plan.duration_days)

                        user.subscription_active = True
                        user.save()

                # Process associated order
                order_number = amount_checkout.order.order_number if amount_checkout.order else None
                print('Order Number', order_number)
                print('amount_checkout.order', amount_checkout.order)
                if order_number:
                    order = Order.objects.get(order_number=order_number)
                    order.status = 'Paid'
                    order.is_ordered = True
                    order.save()

                    # Update OrderProducts and clean cart
                    ordered_products = OrderProduct.objects.filter(order=order)
                    for product in ordered_products:
                        product.ordered = True
                        product.save()

                    if order.user:
                        CartItem.objects.filter(user=order.user).delete()
                        logger.info(f"Cart items deleted for authenticated user: {order.user}")
                    elif order.is_guest and order.cart_id:
                        CartItem.objects.filter(cart=order.cart_id).delete()
                        logger.info(f"Cart items deleted for guest user with cart_id: {order.cart_id}")

                else:
                    logger.error(f"No user associated with AmountCheckout ID: {amount_checkout_id}")
            elif event_type == 'checkout.failed':
                amount_checkout.on_failure()

                # Check and mark affiliate commission as failed
                affiliate_commission = AffiliateCommission.objects.filter(commission_amount=Decimal(str(amount_checkout.amount))).first()
                if affiliate_commission:
                    affiliate_commission.is_paid = False
                    affiliate_commission.save()
                    logger.info(f"Affiliate commission for {affiliate_commission.affiliate.user.email} marked as failed.")

                # Process associated order
                order_number = amount_checkout.order.order_number if amount_checkout.order else None
                print('Order Number', order_number)
                print('amount_checkout.order', amount_checkout.order)
                if order_number:
                    order = Order.objects.get(order_number=order_number)
                    order.status = 'Cancelled'
                    order.is_ordered = False
                    order.save()

                    # Update OrderProducts and clean cart
                    ordered_products = OrderProduct.objects.filter(order=order)
                    for product in ordered_products:
                        product.ordered = True
                        product.save()
            elif event_type == 'checkout.canceled':
                amount_checkout.on_cancel()

                # Check and mark affiliate commission as canceled
                affiliate_commission = AffiliateCommission.objects.filter(commission_amount=Decimal(str(amount_checkout.amount))).first()
                if affiliate_commission:
                    affiliate_commission.is_paid = False
                    affiliate_commission.save()
                    logger.info(f"Affiliate commission for {affiliate_commission.affiliate.user.email} marked as canceled.")

                # Process associated order
                order_number = amount_checkout.order.order_number if amount_checkout.order else None
                print('Order Number', order_number)
                print('amount_checkout.order', amount_checkout.order)
                if order_number:
                    order = Order.objects.get(order_number=order_number)
                    order.status = 'Cancelled'
                    order.is_ordered = False
                    order.save()

                    # Update OrderProducts and clean cart
                    ordered_products = OrderProduct.objects.filter(order=order)
                    for product in ordered_products:
                        product.ordered = True
                        product.save()
            elif event_type == 'checkout.expired':
                amount_checkout.on_expire()

                # Check and mark affiliate commission as expired
                affiliate_commission = AffiliateCommission.objects.filter(commission_amount=Decimal(str(amount_checkout.amount))).first()
                if affiliate_commission:
                    affiliate_commission.is_paid = False
                    affiliate_commission.save()
                    logger.info(f"Affiliate commission for {affiliate_commission.affiliate.user.email} marked as expired.")

                # Process associated order
                order_number = amount_checkout.order.order_number if amount_checkout.order else None
                print('Order Number', order_number)
                print('amount_checkout.order', amount_checkout.order)
                if order_number:
                    order = Order.objects.get(order_number=order_number)
                    order.status = 'Cancelled'
                    order.is_ordered = False
                    order.save()

                    # Update OrderProducts and clean cart
                    ordered_products = OrderProduct.objects.filter(order=order)
                    for product in ordered_products:
                        product.ordered = True
                        product.save()
            else:
                logger.warning(f"Unhandled event type: {event_type}")
        except AmountCheckout.DoesNotExist:
            logger.error(f"No AmountCheckout found for ID: {amount_checkout_id}")

        return JsonResponse({"message": "Webhook processed successfully"}, status=200)
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return HttpResponse("Internal server error", status=500)





