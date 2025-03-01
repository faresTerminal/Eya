from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

