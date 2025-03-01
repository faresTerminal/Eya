


from django.urls import reverse
from django.utils import translation



class AdminLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the current request is for the admin site.
        if reverse('admin:index') in request.path:
            # If it's an admin page, set language to English.
            request.LANGUAGE_CODE = 'en-us'
            request.session[translation.LANGUAGE_SESSION_KEY] = 'en-us'
        
        response = self.get_response(request)
        return response




