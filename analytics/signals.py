# analytics/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order  # Assuming you have an Order model
from .models import OrderAnalytics

@receiver(post_save, sender=Order)
def track_order_analytics(sender, instance, created, **kwargs):
    if created and instance.status == 'completed':  # Assuming 'completed' is a status
        OrderAnalytics.objects.create(
            order_id=instance.id,
            total_value=instance.total_price,  # Adjust based on your Order model
            user=instance.user,
            payment_method=instance.payment_method,
            completed=True,
        )
