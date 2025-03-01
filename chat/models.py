from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from store.models import Product
from accounts.models import Account

User = get_user_model()

class Conversation(models.Model):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='seller_conversations')
    buyer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='buyer_conversations')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation from {self.seller.username} and {self.buyer.username}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    

    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"


class Notification(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - Message ID: {self.message.id}"
