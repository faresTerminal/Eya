from django.shortcuts import redirect
from django.urls import reverse
from accounts.models import Account
from django.utils import timezone

class SubscriptionMiddleware:
    """
    Middleware to check if the user has an active subscription or trial.
    If not, redirect them to the subscription plans page when they try to access restricted pages (e.g. Analytics).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that should be excluded from the subscription check
        excluded_urls = [
            reverse('payment:trial_expired'),  # Trial expired page
            reverse('payment:subscription_needed'),  # Subscription needed page
            reverse('blog'),  # Blog page or any other page you want to always allow
        ]
        
        # Skip the subscription check for URLs in the excluded_urls list
        if request.path in excluded_urls:
            return self.get_response(request)

        # List of URLs that belong to the Analytics app or any restricted pages
        restricted_urls = [
           '/en/analytics/',  # Replace with your actual analytics page URL
           '/ar/analytics/',  # Replace with your actual analytics page URL
           '/fr/analytics/',  # Replace with your actual analytics page URL
           '/en/accounts/printing/',
           '/fr/accounts/printing/',
           '/ar/accounts/printing/',
           '/en/products/add-product/',
           '/fr/products/add-product/',
           '/ar/products/add-product/',
           
          
            
        ]
        
        # If the user tries to access a restricted URL (e.g., Analytics), check subscription status
        if request.path in restricted_urls:
            # Check if the user has an active subscription or trial
            if not self.has_active_subscription_or_trial(request.user):
                return redirect('payment:subscription_needed')  # Redirect to subscription needed page

        # Continue with the response
        response = self.get_response(request)
        return response

    def has_active_subscription_or_trial(self, user):
        """
        Check if the user has an active subscription or trial.
        This function returns True if the user has an active subscription or valid trial.
        """
        if user.is_authenticated:
            # Check if the user has an active subscription or trial
            if user.is_trial and timezone.now() <= user.trial_end_date:
                return True  # Trial is still valid
            if user.subscription_active:
                return True  # User has an active subscription
        return False  # No active subscription or trial
