"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.conf.urls.i18n import i18n_patterns # for transilation
from django.conf.urls.i18n import set_language
from django.utils.translation import activate
from django.conf.urls import handler500

# Activate the admin language
activate('en')
handler404 = 'ecommerce.views.custom_404'
handler500 = 'ecommerce.views.server_error'  # Replace 'myapp' with your app name


urlpatterns = [

    # ... your non-translatable URLs ...

    path('admin/', admin.site.urls),
    
    
    
   

    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += i18n_patterns(


    # ... your translatable URLs ...
    path('', views.home, name='home'),
    path('store/', include('store.urls')),
    path('blog/', include('blog.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('category/', include('category.urls')),
    path('social/', include('social.urls')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('newsletter/', include('newsletter.urls')),
    path('products/', include('products.urls')),
    path('printing/', include('printing.urls')),
    path('stock/', include('stock.urls')),
    






)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





