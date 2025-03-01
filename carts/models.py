from django.db import models
from store.models import Product, Variation
from accounts.models import Account


# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    variation_id = models.IntegerField(blank=True, null=True)
    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    dis_coupon = models.FloatField(blank=True, default=0)
    
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        variation = self.variations.first()

        if variation and variation.clearance_price and variation.clearance_price > 0:
            base_price = variation.clearance_price
        elif variation and variation.price:
            base_price = variation.price
        else:
            # Handle the case when neither clearance_price nor price is available
            base_price = 0

        total = base_price * self.quantity

        # Apply discount as a percentage if dis_coupon is greater than zero
        if self.dis_coupon and self.dis_coupon > 0:
            discount = (self.dis_coupon / 100) * total
            total -= discount

        return max(total, 0)


    def save(self, *args, **kwargs):
        # Call the parent class's save method to save the CartItem
        super().save(*args, **kwargs)

        # Set the featured field of the related Product to True
        self.product.featured = True
        self.product.save()


        

    def __unicode__(self):
        return self.product