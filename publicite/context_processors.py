# publicite/context_processors.py

from .models import SlideAd, ShowAd

def ads(request):
    """
    Context processor that adds active slide and show ads to the context of every template.
    """
    slide_ads = SlideAd.objects.filter(is_active=True)
    show_ads = ShowAd.objects.filter(is_active=True)
    return {
        'slide_ads': slide_ads,
        'show_ads': show_ads,
    }
