from django.db import models

class EmailSubscription(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
    	return self.email
