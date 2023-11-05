# comparison/models.py

from django.db import models
from store.models import Product  

class Comparison(models.Model):
    product1 = models.ForeignKey(Product, related_name='product1_comparisons', on_delete=models.CASCADE)
    product2 = models.ForeignKey(Product, related_name='product2_comparisons', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    # Add any additional fields or methods as needed

    def __str__(self):
        return f"Comparison between {self.product1} and {self.product2}"
