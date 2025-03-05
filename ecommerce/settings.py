"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from django.utils.translation import gettext_lazy as _  # For adding multilingual support (e.g., en, fr, ar)
from pathlib import Path  # For handling filesystem paths
import os  # For interacting with the operating system
import pdfkit  # For PDF generation
from django.contrib.messages import constants as messages  # For customizing message tags
from decouple import config  # For loading environment variables from a .env file

# Base directory of the project
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Secret key (should be kept secret and loaded securely in production)
SECRET_KEY = config('SECRET_KEY')

# Debug mode (disable in production for security)
DEBUG = True

# List of allowed hosts (update with your domain in production)
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'souqify-cb4979b2c021.herokuapp.com']

USE_I18N = True

RECAPTCHA_PUBLIC_KEY = '6Lf2yuYqAAAAABV8rnoclnyhYeGrLXmKu04jeG9p'
RECAPTCHA_PRIVATE_KEY = '6Lf2yuYqAAAAAM_FnhQagvEi4umIaAVR7CZB5R3T'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # This should be the default
SESSION_COOKIE_NAME = 'sessionid'


# Thumbnail engine settings for image processing
THUMBNAIL_ENGINE = 'sorl.thumbnail.engines.pil_engine.Engine'

# Installed apps
INSTALLED_APPS = [
    # Default Django apps
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',


    # Third-party apps
    'allauth',  # Django Allauth for authentication
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',  # Facebook OAuth
    'allauth.socialaccount.providers.google',  # Google OAuth
    'sorl.thumbnail',  # Thumbnail image processing
    'tinymce',  # Rich text editor
    'analytical',  # For Google Analytics and Facebook Pixel
    'robots',
    'widget_tweaks',
    'channels',
    

    # Custom apps
    'category',
    'accounts',
    'store',
    'carts',
    'orders',
    'products',
    'blog',
    'newsletter',
    'printing',
    'social',
    'social_django',  # For social authentication
    'cities_light',  # For managing geographical data (cities, regions)
    'stock',
    'marketing',
    'chat',
    'notification',
    'social_sharing',
    'django.contrib.humanize',  # For formatting numbers, dates, etc.
    'analytics',  # Custom analytics app
    'chartjs',  # For rendering charts
    'seo',  # Custom app for SEO & metadata
    'payment',
    'affiliate',
    'publicite',
    

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Provides security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware',  # Manages sessions
    'django.middleware.common.CommonMiddleware',  # Common middleware for request processing
    'django.middleware.csrf.CsrfViewMiddleware',  # Protects against CSRF attacks
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Handles authentication
    'payment.middleware.SubscriptionMiddleware',  # Move subscription check before Authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Enables message framework
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Prevents clickjacking attacks
    'accounts.middleware.AdminLocaleMiddleware',  # Custom middleware for locale handling
    'django.middleware.locale.LocaleMiddleware',  # Enables localization
    'django.contrib.sites.middleware.CurrentSiteMiddleware',  # Handles multi-site functionality
    'analytics.middleware.AnalyticsMiddleware',  # Custom middleware for analytics
    
]

# Redirect URL after login
LOGIN_REDIRECT_URL = "/"

# Root URL configuration
ROOT_URLCONF = 'ecommerce.urls'

# HTTP protocol for account-related operations
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Default site ID for multi-site setups
SITE_ID = 1

# Templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],  # Location of template files
        'APP_DIRS': True,  # Enable app-specific templates
        'OPTIONS': {
            'context_processors': [  # Injects variables into templates
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links',
                'carts.context_processors.counter',
                'carts.context_processors.Items',
                'store.context_processors.wishlist_count',
                'accounts.context_processors.user_profile_picture',
                'orders.context_processors.seller_order_count',
                'notification.context_processors.notifications',
                'chat.context_processors.user_conversations',
                'accounts.context_processors.social_links',
                'django.template.context_processors.i18n',
                'social.context_processors.facebook_pixels',
                'publicite.context_processors.ads',
            ],
        },
    },
]

# WSGI and ASGI application paths
WSGI_APPLICATION = 'ecommerce.wsgi.application'
ASGI_APPLICATION = 'ecommerce.asgi.application'

# Custom user model
AUTH_USER_MODEL = 'accounts.Account'

# Database configuration (SQLite for development; switch to PostgreSQL in production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization settings
TIME_ZONE = 'UTC'
USE_I18N = True  # Enables translation
USE_L10N = False  # Disable Django's legacy date formatting
USE_TZ = True  # Enables timezone support
LANGUAGE_CODE = 'en'  # Default language
LANGUAGES = [
    ('en', _('English')),  # English
    ('ar', _('Arabic')),  # Arabic
    ('fr', _('French')),  # French
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]  # Path for translation files

# Static files settings
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'assets')]

# Add this line:
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory to collect static files

# Media files settings
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Message tags customization
MESSAGE_TAGS = {
    messages.ERROR: 'danger',  # Map Django error messages to Bootstrap's "danger" class
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_PASSWORD')
EMAIL_USE_TLS = True  # Enable secure email communication

# TinyMCE rich text editor configuration
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 600,
    'menubar': True,
    'plugins': 'advlist autolink lists link image charmap print preview anchor',
    'toolbar': 'a11ycheck | formatselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
}

# Authentication backends (Django Allauth and default Django auth)
AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# Social account providers (Google and Facebook settings)
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    },
    'facebook': {
        'SCOPE': ['email', 'public_profile'],
        'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
    },
}

# Facebook API credentials
SOCIAL_AUTH_FACEBOOK_KEY = '1495369231175460'
SOCIAL_AUTH_FACEBOOK_SECRET = 'b5fb08425203a3c4460c676d87f2ec91'


ROBOTS_USE_SITEMAP = True  # Automatically adds your sitemap link to robots.txt


STRIPE_API_KEY = 'sk_test_51QUw7kDmN7cuhqUlHvXXUH3hfgvPMDoCM9svj0PjFpcScPYfYZBZmqFRocNf8KQFZOuHk9k2bP72AqmzS6OLc7X300GsilPRAR'


# settings.py

STRIPE_SECRET_KEY = 'sk_test_51QUw7kDmN7cuhqUlHvXXUH3hfgvPMDoCM9svj0PjFpcScPYfYZBZmqFRocNf8KQFZOuHk9k2bP72AqmzS6OLc7X300GsilPRAR'
STRIPE_PUBLISHABLE_KEY = 'pk_test_51QUw7kDmN7cuhqUlwB8heCFmYOTfWwEC8ZJMygt9EuX6NeBn8YLjgFW3V1YcrhG21PYIj5tBb5GwvyPeNyacBfAz007NDy7MIo'







# settings.py

# settings.py

import environ
from pathlib import Path

# Initialize environ to read .env variables
env = environ.Env()

# Base directory of the project (path where settings.py is located)
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the .env file (should be in the root of the project)
environ.Env.read_env(str(BASE_DIR / ".env"))


# Now you can access your environment variables
CHARGILY_KEY = env("CHARGILY_KEY")
CHARGILY_SECRET = env("CHARGILY_SECRET")
CHARGILY_URL = "https://pay.chargily.net/test/api/v2"




# settings.py
SITE_URL = "https://e183-105-235-133-231.ngrok-free.app"  # Replace with your actual site URL




