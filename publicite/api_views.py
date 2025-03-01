# publicite/api_views.py

# publicite/api_views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Advertisement
from .serializers import AdvertisementSerializer
from django.utils import timezone
import random

@api_view(['GET'])
def get_random_ad(request):
    """Fetch a random active ad via API."""
    active_ads = Advertisement.objects.filter(
        is_active=True, 
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    
    # Check if there are any active ads
    if active_ads.exists():
        # Pick a random ad
        ad = random.choice(active_ads)
        ad.increment_impressions()  # Track ad impressions
        serializer = AdvertisementSerializer(ad)
        return Response(serializer.data)
    
    # If no active ads found
    return Response({"error": "No active ads"}, status=404)

