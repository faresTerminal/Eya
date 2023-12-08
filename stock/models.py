from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from store.models import Product, Variation
from accounts.models import Account

class StockHistory(models.Model):
    product = models.ForeignKey(Variation, on_delete=models.CASCADE, default='ert')
    user   = models.ForeignKey(Account, on_delete=models.CASCADE)
    change_date = models.DateTimeField(default=timezone.now)
    quantity_before_change = models.PositiveIntegerField()
    quantity_after_change = models.PositiveIntegerField()
    reason_for_change = models.TextField()

    def __str__(self):
        return f"{self.product.product.product_name} - {self.product.color} - {self.product.size} - {self.change_date}"

    def unit_change(self):
        return self.quantity_after_change - self.quantity_before_change


class Adjustment_StockHistory(models.Model):
    product = models.ForeignKey(Variation, on_delete=models.CASCADE, default='erqq')
    adjusted_by = models.ForeignKey(Account, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=10)  # 'add' or 'subtract'
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.adjustment_type} {self.quantity} for {self.product.product.product_name} at {self.timestamp}"



