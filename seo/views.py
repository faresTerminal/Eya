from django.shortcuts import render

# Create your views here.
from .models import Metadata
from django.contrib.contenttypes.models import ContentType
from store.models import Product

def get_metadata_for_object(obj):
    content_type = ContentType.objects.get_for_model(obj)
    metadata = Metadata.objects.filter(content_type=content_type, object_id=obj.id).first()
    
    if not metadata:
        default_meta = get_default_metadata()
        return default_meta

    return metadata



def get_default_metadata():
    return {
        "title": "Your E-Commerce Platform",
        "description": "Shop the best products at amazing prices.",
        "keywords": "shopping, ecommerce, buy online",
        "canonical_url": "https://www.yourdomain.com",
    }


def generate_product_json_ld(product):
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.product_name,
        "image": [product.images.url],
        "description": product.description,
        "brand": {
            "@type": "Brand",
            "name": product,
        },
        "sku": product.sku,
        "offers": {
            "@type": "Offer",
            "url": product.get_absolute_url(),
            "priceCurrency": "USD",
            "price": product,
            "availability": "https://schema.org/InStock",
        },
    }

