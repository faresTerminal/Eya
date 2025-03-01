from django.db import models
from accounts.models import Account
from store.models import Product, Variation
from phone_field import PhoneField
from cities_light.models import City, Region
import uuid
from django.utils import timezone



class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Paid', 'Paid'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    SHIPPING_METHOD_CHOICES = (
        ('home', 'Home Delivery'),
        ('pickup', 'Pick Up from Delivery Bureau'),
    )
    Delivery_Company_CHOICES = (
        ('yalidine', 'Yali Dine'),
        ('KaziTour', 'Kazi Tour'),
        ('turktour', 'Turk Tour'),
        ('expres', 'Expres'),
        ('rapidtour', 'Rapid Tour'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cib', 'Credit Bank Card (CIB)'),
        ('edahabia', 'Card Manitique'),
        ('cod', 'Cash on Delivery'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    order_number = models.CharField(max_length=20)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=20)
    order_note = models.CharField(max_length=100, blank=True)
    shipping_total = models.FloatField()
    order_total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    shipping_method = models.CharField(
        max_length=10,
        choices=SHIPPING_METHOD_CHOICES,
        default='home',  # Default to Home Delivery
    )
     # Add a pickup_location field if the user selects 'pickup' shipping method
    pickup_location = models.CharField(
        max_length=10,
        choices=Delivery_Company_CHOICES,
        default='Home'
          # Default to Home Delivery
    )
     # New field to store the payment method selected by the user
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='cod',  # Default to Cash on Delivery
    )
    purchased_through_affiliate = models.ForeignKey(
        'affiliate.Affiliate', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='affiliate_orders'
    )

    promotion_discount = models.FloatField(null=True, blank=True)
    coupon_discount = models.FloatField(null=True, blank=True)
    subtotal = models.FloatField(null=True, blank=True)  # New field for subtotal
    total_shipping_cost = models.FloatField(null=True, blank=True)  # New field for shipping cost
    #Field to Distinguish Anonymous and Logged-in Users
    is_guest = models.BooleanField(default=False, null=True)

    download_expiration = models.DateTimeField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_download_removed = models.BooleanField(default=False)  # Track if download is removed

    # Method to check if the download is expired
    def is_download_expired(self):
      if self.download_expiration is None:
        return False  # or return True based on your logic, i.e., treat orders without expiration as expired
      return timezone.now() > self.download_expiration


    # Method to check if the user has exceeded the download limit
    def has_reached_download_limit(self, limit=3):  # Default limit is 3 downloads
        return self.download_count >= limit

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def full_address(self):
        return f'{self.address_line_1}'

    def __str__(self):
        return self.first_name





class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)  # Optional, for the wilaya_code

    def __str__(self):
        return self.name



class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, related_name='cities', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name




class City_Region(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    



