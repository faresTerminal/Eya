from django.conf import settings
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin


class ForceInEnglish(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> None:
        if request.path.startswith("/admin"):
            request.COOKIES[settings.LANGUAGE_COOKIE_NAME] = "en"
