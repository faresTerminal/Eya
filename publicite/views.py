# publicite/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
import random
from .models import Advertisement

def get_active_ad():
    """Retrieve a random active ad."""
    active_ads = Advertisement.objects.filter(is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now())
    return random.choice(active_ads) if active_ads else None

def show_ad(request):
    """Return a random ad as JSON."""
    ad = get_active_ad()
    if ad:
        ad.increment_impressions()  # Track ad views
        return JsonResponse({
            "title": ad.title,
            "type": ad.ad_type,
            "image_url": ad.image.url if ad.image else None,
            "video_url": ad.video.url if ad.video else None,
            "link": ad.link,
            "impressions": ad.impressions,
        })
    return JsonResponse({"error": "No active ads available"}, status=404)



