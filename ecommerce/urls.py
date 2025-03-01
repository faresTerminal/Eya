"""
ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information, please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/

Examples:
Function views:
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views:
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf:
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include  # Used for including other URL configurations
from . import views  # Import views from the current directory
from django.conf.urls.static import static  # For serving media files during development
from django.conf import settings  # Import settings module for static/media configuration
from django.conf.urls.i18n import i18n_patterns  # For supporting URL translations
from django.utils.translation import activate  # For activating a specific language

# urls.py

from django.contrib.sitemaps.views import sitemap

from .sitemaps import ProductSitemap

sitemaps = {
    'products': ProductSitemap,
    # You can add more sitemaps if needed (e.g., for other models)
}


# Activate the admin language (English in this case)
activate('en')

# Custom error handlers
handler404 = 'ecommerce.views.custom_404'  # Custom view for handling 404 errors
handler500 = 'ecommerce.views.server_error'  # Custom view for handling 500 errors

# Main URL patterns (non-translatable URLs)
urlpatterns = [

    path('admin/', admin.site.urls),  # Admin site URL
    path('robots.txt', include('robots.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files during development

# Translatable URL patterns
urlpatterns += i18n_patterns(
    path('', views.home2, name='home2'),
    path('', views.home, name='home'),  # Home page
      # Home page
    path('store/', include('store.urls')),  # Store app URLs
    path('blog/', include('blog.urls')),  # Blog app URLs
    path('cart/', include('carts.urls')),  # Cart app URLs
    
    path('accounts/', include('accounts.urls')),  # Custom account-related URLs
    #path('accounts/', include('allauth.urls')),  # Allauth for authentication (e.g., login, signup)
    path('orders/', include('orders.urls')),  # Order management URLs
    path('analytics/', include('analytics.urls')),  # Analytics-related URLs
    path('category/', include('category.urls')),  # Category management URLs
    path('social/', include('social.urls')),  # Social features URLs
    path('auth/', include('social_django.urls', namespace='social')),  # Social Django URLs
    path('newsletter/', include('newsletter.urls')),  # Newsletter app URLs
    path('products/', include('products.urls')),  # Product management URLs
    path('printing/', include('printing.urls')),  # Printing-related URLs
    path('stock/', include('stock.urls')),  # Stock management URLs
    path('marketing/', include('marketing.urls')),  # Marketing-related URLs
    path('chat/', include('chat.urls')),  # Chat feature URLs
    path('notification/', include('notification.urls')),  # Notification system URLs
    path('social_sharing/', include('social_sharing.urls')),  # Social sharing URLs
    path('robots.txt', include('robots.urls')),
    path('payment/', include('payment.urls')),
    path('affiliate/', include('affiliate.urls')),
    path('publicite/', include('publicite.urls')),
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files again for translated URLs



