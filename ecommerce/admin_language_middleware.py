# admin_language_middleware.py

class AdminLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the admin site
        if request.path.startswith('/admin/'):
            request.LANG = 'en'  # Set the language to 'en' for the admin site
        response = self.get_response(request)
        return response
