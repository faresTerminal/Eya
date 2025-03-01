# publicite/urls.py

from django.urls import path
from .views import show_ad
from .api_views import get_random_ad

urlpatterns = [
    path('show/', show_ad, name='show_ad'),
    path('api/random/', get_random_ad, name='api_random_ad'),
    

]
