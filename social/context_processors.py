from .models import FacebookPixel

def facebook_pixels(request):
    if request.user.is_authenticated:
        user_pixels = FacebookPixel.objects.filter(user=request.user)
        return {'facebook_pixels': user_pixels}
    return {}
