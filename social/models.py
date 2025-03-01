from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account

class FacebookPixel(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='facebook_pixels')
    pixel_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Add the name field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.pixel_id})"

