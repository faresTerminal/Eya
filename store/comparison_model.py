from django.db import models
from ..models import Product
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count


class Comparison(models.Model):
    products = models.ManyToManyField(Product, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comparison #{self.pk}"