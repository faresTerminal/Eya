from django.apps import AppConfig


class AffiliateConfig(AppConfig):
    name = 'affiliate'

    def ready(self):
        import affiliate.signals  # Import the signal handler
