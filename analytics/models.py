# analytics/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Account
from store.models  import Product


class PageView(models.Model):
    url = models.URLField()  # URL of the page viewed
    user = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)  # User who viewed the page
    timestamp = models.DateTimeField(default=timezone.now)  # Time the page was viewed
    session_key = models.CharField(max_length=40, null=True, blank=True)  # Assuming you want to store the session key

    def __str__(self):
        return f"Page view by {self.user if self.user else 'anonymous'} on {self.timestamp}"


class OrderAnalytics(models.Model):
    order_id = models.CharField(max_length=50)  # Unique ID for the order
    total_value = models.DecimalField(max_digits=10, decimal_places=2)  # Total value of the order
    created_at = models.DateTimeField(default=timezone.now)  # Order creation time
    completed = models.BooleanField(default=False)  # Whether the order was completed
    user = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)  # User who placed the order
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=None)
    #payment_method = models.CharField(max_length=50)  # Payment method used
    quantity = models.PositiveIntegerField(default=0, blank=False)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promotion_discount = models.FloatField(null=True, blank=True)
    coupon_discount = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"OrderAnalytics({self.order_id}, {self.total_value}, {self.created_at})"


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, null=True, blank=True, on_delete=models.CASCADE)  # Track user if logged in
    ip_address = models.GenericIPAddressField()  # Optionally, track IP address if no user is logged in
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"View of {self.product.product_name} by {self.user or self.ip_address} at {self.viewed_at}"