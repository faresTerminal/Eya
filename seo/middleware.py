from .models import Metadata
from django.contrib.contenttypes.models import ContentType

class SEOMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip if it's not an HTML response
        if not response.get('Content-Type', '').startswith('text/html'):
            return response

        # Get the metadata (if any)
        content_type = ContentType.objects.get(app_label='your_app', model='your_model')
        metadata = Metadata.objects.filter(content_type=content_type).first()

        if metadata:
            response.content = response.content.decode('utf-8').replace(
                '</head>',
                f"""
                <meta name="description" content="{metadata.description}">
                <meta name="keywords" content="{metadata.keywords}">
                <link rel="canonical" href="{metadata.canonical_url}">
                </head>
                """
            ).encode('utf-8')

        return response
