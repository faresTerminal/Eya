# publicite/models.py
from django.db import models
from django.utils import timezone

class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=255)
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default='image')
    image = models.ImageField(upload_to='ads/images/', null=True, blank=True)
    youtube_link = models.URLField(null=True, blank=True, help_text="YouTube video URL")  # New field for YouTube video link
    link = models.URLField(blank=True, help_text="Optional URL to redirect when clicked")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    impressions = models.PositiveIntegerField(default=0, help_text="Number of times the ad has been viewed")

    def __str__(self):
        return self.title

    def is_active_now(self):
        """Check if the ad is currently active based on date range."""
        return self.is_active and self.start_date <= timezone.now() <= self.end_date

    def increment_impressions(self):
        """Increment the impressions count when an ad is viewed."""
        self.impressions += 1
        self.save()



# publicite/models.py

class SlideAd(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/slide/', null=True, blank=True)
    link = models.URLField(blank=True, help_text="Optional URL to redirect when clicked")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def __str__(self):
        return self.title

    def is_active_now(self):
        """Check if the slide ad is currently active based on date range."""
        return self.is_active and self.start_date <= timezone.now() <= self.end_date


# publicite/models.py

class ShowAd(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/show/', null=True, blank=True)
    link = models.URLField(blank=True, help_text="Optional URL to redirect when clicked")
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def __str__(self):
        return self.title

    def is_active_now(self):
        """Check if the show ad is currently active based on date range."""
        return self.is_active and self.start_date <= timezone.now() <= self.end_date
