
from django.db import models
from accounts.models import Account
from django.contrib.auth.models import User
from accounts.models import Account
from orders.models import Order
class PaymentGateway(models.TextChoices):
    CHARGILY = 'Chargily', 'Chargily'
   

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    duration_days = models.IntegerField()  # Plan duration in days (e.g., 90 for 3 months, 180 for 6 months, 365 for 1 year)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)  # New field to check if the plan is active

    def __str__(self):
        return self.name








from django.db import models
from django.contrib.auth import get_user_model
from chargily_pay.entity import Checkout

User = get_user_model()


class AmountCheckout(models.Model):
    class PAYMENT_STATUS(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"
        EXPIRED = "EXPIRED", "Expired"

    class PAYMENT_METHOD(models.TextChoices):
        EDAHABIA = "edahabia", "Edahabia"
        CIB = "cib", "CIB"

    class LOCALE(models.TextChoices):
        ENGLISH = "en", "English"
        ARABIC = "ar", "Arabic"
        FRENCH = "fr", "French"

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(
        Order,  
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='amount_checkouts'
    )
    entity_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD.choices, default=PAYMENT_METHOD.EDAHABIA
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    locale = models.CharField(max_length=2, choices=LOCALE.choices, default=LOCALE.FRENCH)
    status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS.choices, default=PAYMENT_STATUS.PENDING
    )
    checkout_url = models.URLField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def on_paid(self):
        self.status = self.PAYMENT_STATUS.PAID
        self.save()

    def on_failure(self):
        self.status = self.PAYMENT_STATUS.FAILED
        self.save()

    def on_cancel(self):
        self.status = self.PAYMENT_STATUS.CANCELED
        self.save()

    def on_expire(self):
        self.status = self.PAYMENT_STATUS.EXPIRED
        self.save()

    def to_entity(self) -> Checkout:
      entity = {
        "amount": self.amount,
        "currency": "dzd",
        "success_url": "success_url",
        "payment_method": self.payment_method,
        "customer_id": self.customer.id if self.customer else None,
        "failure_url": None,
        "webhook_endpoint": None,
        "description": self.description,
        "locale": self.locale,
        "pass_fees_to_customer": False,
      }
      return Checkout(**entity)



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    gateway = models.CharField(max_length=50, choices=PaymentGateway.choices, default=PaymentGateway.CHARGILY)
    amount = models.IntegerField()
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=255, unique=True)

    payment_link = models.URLField(max_length=500, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=AmountCheckout.PAYMENT_STATUS.choices,
        default=AmountCheckout.PAYMENT_STATUS.PENDING,
    )

    def __str__(self):
        return f"Payment {self.transaction_id} by {self.user.username}"

class Invoice(models.Model):
    payment = models.OneToOneField(AmountCheckout, on_delete=models.CASCADE, related_name='invoice')
    issued_date = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='invoices/', blank=True, null=True)  # Store generated invoices

    def __str__(self):
        return f"Invoice for {self.payment.entity_id}"