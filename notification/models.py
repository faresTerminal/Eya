from django.db import models
from django.contrib.auth.models import User
from chat.models import Conversation  # Import your chat app's Conversation model
from accounts.models import Account


class Notification(models.Model):
    sender = models.ForeignKey(Account, related_name="sent_notifications", on_delete=models.CASCADE)
    recipient = models.ForeignKey(Account, related_name="received_notifications", on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True)  # Link to the conversation
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    profile_picture_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Notification from {self.sender.username} to {self.recipient.username}"

