# context_processors.py

from .models import Wishlist

def wishlist_count(request):
    if request.user.is_authenticated:
        wishlist_items_count = Wishlist.objects.filter(user=request.user).count()
    else:
        wishlist_items_count = 0
    return {'wishlist_items_count': wishlist_items_count}

