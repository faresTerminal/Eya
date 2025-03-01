# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from notification.models import Notification

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created:
        # Determine the recipient of the notification (the other party in the conversation)
        recipient = instance.conversation.buyer if instance.sender == instance.conversation.seller else instance.conversation.seller
        
        # Get the sender's profile picture URL
        profile_picture_url = instance.sender.userprofile.profile_picture.url if instance.sender.userprofile.profile_picture else '/static/default_profile_picture.png'
        
        # Create the notification
        Notification.objects.create(
            sender=instance.sender,
            recipient=recipient,
            conversation=instance.conversation,
            message=f"New message from {instance.sender.full_name()}",
            url=f"/chat/{instance.conversation.id}/",
            profile_picture_url=profile_picture_url,  # Set profile picture URL
        )


