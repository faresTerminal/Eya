import uuid
import requests
from django.conf import settings
import uuid
import requests
from django.conf import settings
from django.utils.timezone import now
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from orders.models import Order, OrderProduct
from payment.models import SubscriptionPlan, AmountCheckout, Payment, Invoice





class PaymentService:
    @staticmethod
    def create_checkout(order, payment_method, locale):
        """
        Create a checkout session for an order using Chargily API.
        """
        customer_payload = {
           "name": order.full_name(),
           "phone": order.phone,
           "address": {
           "country": "DZ",
           "state": "Algiers",
           "address": order.address_line_1,  # Use the address directly from the order
           },
        }

        # Check if the user is anonymous
        if not order.user or order.is_guest:
              # Use a placeholder email for anonymous users
              customer_payload["email"] = f"guest_{order.first_name}@EcoHome.com"
        else:
              # Use the registered user's email
              customer_payload["email"] = order.user.email


        customer_url = f"{settings.CHARGILY_URL}/customers"
        headers = {
            "Authorization": f"Bearer {settings.CHARGILY_SECRET}",
            "Content-Type": "application/json",
        }

        try:
            customer_response = requests.post(customer_url, json=customer_payload, headers=headers)
            if customer_response.status_code != 200:
                raise Exception(f"Failed to create customer: {customer_response.text}")

            customer_id = customer_response.json().get("id")

            ordered_products = OrderProduct.objects.filter(order=order)
            for product in ordered_products:
                image_url = (
                    product.product.images.url
                    if product.product.images.url.startswith("https")
                    else f"{settings.SITE_URL}{product.product.images.url}"
                )
                product_payload = {
                    "name": product.product.product_name,
                    "description": product.product.description,
                    "images": [image_url],
                    "metadata": {"product_id": f"{product.product.id}"},
                }
                print('Product information:', product_payload)
                product_url = f"{settings.CHARGILY_URL}/products"
                product_response = requests.post(product_url, json=product_payload, headers=headers)

                if product_response.status_code != 200:
                    raise Exception(f"Failed to add product {product.product.product_name}: {product_response.text}")

            entity_id = str(uuid.uuid4())

            checkout_payload = {
                "amount": order.order_total,
                "currency": "dzd",
                "payment_method": order.payment_method,
                "success_url": f"{settings.SITE_URL}/orders/success/{order.transaction_id}/",
                "failure_url": f"{settings.SITE_URL}/payment/failure",
                "webhook_endpoint": f"{settings.SITE_URL}/en/payment/webhook/",
                "description": f"Payment for Order #{order.product.product_name}",
                "locale": locale,
                "customer_id": customer_id,
            }

            checkout_url = f"{settings.CHARGILY_URL}/checkouts"
            checkout_response = requests.post(checkout_url, json=checkout_payload, headers=headers)

            if checkout_response.status_code == 200:
                checkout_data = checkout_response.json()
                checkout_url = checkout_data.get("checkout_url")

                AmountCheckout.objects.create(
                    amount=order.order_total,
                    entity_id=order.transaction_id,
                    payment_method=payment_method,
                    customer=order.user,
                    description=checkout_payload["description"],
                    locale=locale,
                    order=order,
                    checkout_url=checkout_url,
                )
                return checkout_url
            else:
                raise Exception(f"Failed to create checkout session: {checkout_response.text}")
        except Exception as e:
            print(f"Error during checkout creation: {e}")
            raise

    @staticmethod
    def create_invoice(checkout_url):
        """
        Create an invoice linked to a payment record.
        """
        return Invoice.objects.create(payment=checkout_url)

   
  

class SubscriptionService:
    @staticmethod
    def get_plan(plan_id):
        """
        Retrieve a subscription plan by its ID.
        """
        return get_object_or_404(SubscriptionPlan, id=plan_id)

    @staticmethod
    def check_user_subscription_status(user):
        """
        Check if the user has an active subscription or trial period.
        """
        if user.is_subscription_valid():
            return redirect('payment:check_active_subscription')

        if user.is_trial and now() > user.trial_end_date:
            user.is_trial = False
            user.save()
            return HttpResponse("Your trial period has expired. Please subscribe to continue.")

        return None

    @staticmethod
    def create_checkout(user, plan, payment_method, locale):
        """
        Create a checkout session for a subscription plan using Chargily API.
        """
        customer_payload = {
            "name": user.username,
            "email": user.email,
            "phone": user.phone_number,
            "address": {
                "country": "dz",
                "state": "Algiers",
                "address": user.userprofile.address_line1,
            },
        }

        customer_url = f"{settings.CHARGILY_URL}/customers"
        headers = {
            "Authorization": f"Bearer {settings.CHARGILY_SECRET}",
            "Content-Type": "application/json",
        }

        try:
            customer_response = requests.post(customer_url, json=customer_payload, headers=headers)
            if customer_response.status_code != 200:
                raise Exception(f"Failed to create customer: {customer_response.text}")

            customer_id = customer_response.json().get("id")
            entity_id = str(uuid.uuid4())

            checkout_payload = {
                "amount": float(plan.price),
                "currency": "dzd",
                "payment_method": payment_method.upper(),
                "success_url": f"{settings.SITE_URL}/payment/success/{entity_id}/",
                "failure_url": f"{settings.SITE_URL}/payment/failure",
                "webhook_endpoint": f"{settings.SITE_URL}/en/payment/webhook/",
                "description": f"Subscription for {plan.name}",
                "locale": locale,
                "customer_id": customer_id,
            }

            chargily_api_url = f"{settings.CHARGILY_URL}/checkouts"
            response = requests.post(chargily_api_url, json=checkout_payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                checkout_url = data.get("checkout_url")

                AmountCheckout.objects.create(
                    amount=plan.price,
                    plan=plan,
                    entity_id=entity_id,
                    payment_method=payment_method,
                    customer=user,
                    description=checkout_payload["description"],
                    locale=locale,
                    checkout_url=checkout_url,
                )
                return checkout_url
            else:
                raise Exception(f"Failed to create payment session: {response.text}")
        except Exception as e:
            print(f"Error during API request: {e}")
            raise






from affiliate.models import AffiliateCommission

import requests
import uuid
from django.conf import settings


class AffiliatePaymentService:
    @staticmethod
    def check_buyer_subscription_status(user):
        """
        Check if the buyer has an active subscription or is a valid customer.
        """
        if not user.is_authenticated:
            return HttpResponse("You must be logged in to proceed with the payment.", status=403)
        return None


    @staticmethod
    def create_checkout_for_affiliate_payment(user, affiliate_commission, payment_method, locale, total_amount=None):
      """
      Create a checkout session for paying affiliate commission using Chargily API.
      """
      if total_amount is None:  # Handling single commission
        total_amount = affiliate_commission.commission_amount
        success_url = f"{settings.SITE_URL}/affiliate/success/{affiliate_commission.id}/"  
      else:  # Handling multiple commissions
        success_url = f"{settings.SITE_URL}/affiliate/success/?total_amount={total_amount}"

      customer_payload = {
        "name": user.username,
        "email": user.email,
        "phone": user.phone_number,
        "address": {
            "country": "dz",
            "state": "Algiers",
            "address": user.userprofile.address_line1,
        },
      }

      # Create customer if needed
      customer_url = f"{settings.CHARGILY_URL}/customers"
      headers = {
        "Authorization": f"Bearer {settings.CHARGILY_SECRET}",
        "Content-Type": "application/json",
      }

      try:
        customer_response = requests.post(customer_url, json=customer_payload, headers=headers)
        if customer_response.status_code != 200:
            raise Exception(f"Failed to create customer: {customer_response.text}")

        customer_id = customer_response.json().get("id")
        entity_id = str(uuid.uuid4())

        # Create checkout payload
        checkout_payload = {
            "amount": float(total_amount),  # Use total amount
            "currency": "dzd",
            "payment_method": "CIB",
            "success_url": success_url,  # ✅ Dynamic Success URL
            "failure_url": f"{settings.SITE_URL}/affiliate/failure",
            "webhook_endpoint": f"{settings.SITE_URL}/payment/webhook/",
            "description": f"Total Affiliate Commission for Affiliate #{user.id}",
            "locale": locale,
            "customer_id": customer_id,
        }

        chargily_api_url = f"{settings.CHARGILY_URL}/checkouts"
        response = requests.post(chargily_api_url, json=checkout_payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            checkout_url = data.get("checkout_url")

            # Save checkout session
            AmountCheckout.objects.create(
                amount=total_amount,
                entity_id=entity_id,
                payment_method=payment_method,
                customer=user,
                description=checkout_payload["description"],
                locale=locale,
                checkout_url=checkout_url,
            )
            return checkout_url
        else:
            raise Exception(f"Failed to create payment session: {response.text}")
      except Exception as e:
        print(f"Error during API request: {e}")
        raise


     


    