# sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from store.models import Product

class ProductSitemap(Sitemap):
    def items(self):
        # Return all published products
        return Product.objects.all()

    def location(self, obj):
        return reverse('product_detail', args=[obj.category.slug, obj.slug])  # Assuming you use slug for product URL

    def lastmod(self, obj):
        # Return the last modified date of the product
        return obj.modified_date  # or created_at depending on your model fields
