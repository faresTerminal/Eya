# analytics/middleware.py
from .models import PageView
from django.utils.timezone import now

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the page view for authenticated users or anonymous users
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        # Make sure the session_key is available
        session_key = request.session.session_key
        if not session_key:
            request.session.create()  # Create a session key if one doesn't exist
        
        # Create the PageView record
        PageView.objects.create(
            url=request.path,
            user=user,
            timestamp=now(),
            session_key=session_key
        )

        response = self.get_response(request)
        return response

