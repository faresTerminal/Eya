from django.db import models
from django.utils import timezone
from store.models import Product, Category
from accounts.models import Account


class Promotion(models.Model):
    title = models.CharField(max_length=100)
    categories = models.ManyToManyField(Category, related_name="promotions")
    image_background= models.ImageField(upload_to='photos/signboard')
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return self.title


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()
    max_uses = models.PositiveIntegerField(null=True, blank=True)  # Max number of times the coupon can be used
    used_count = models.PositiveIntegerField(default=0)  # Track how many times the coupon has been used

    def is_valid(self):
        """
        Check if the coupon is valid, active, and hasn't expired.
        Also check if the max usage limit hasn't been reached.
        """
        is_under_limit = (self.max_uses is None or self.used_count < self.max_uses)
        return self.is_active and timezone.now() < self.expiration_date and is_under_limit

    def increment_usage(self):
        """Increment the used_count when a coupon is successfully applied."""
        self.used_count += 1
        self.save()

    def __str__(self):
        return self.code

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('coupon', 'user')


