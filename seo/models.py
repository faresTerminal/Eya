from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from jsonfield import JSONField


class Metadata(models.Model):
    title = models.CharField(max_length=255, help_text="SEO Title for the page.")
    description = models.TextField(help_text="Meta description for the page.")
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords.")
    canonical_url = models.URLField(blank=True, null=True, help_text="Canonical URL for the page.")
    
    # Open Graph Metadata
    og_title = models.CharField(max_length=255, blank=True, help_text="Open Graph title.")
    og_description = models.TextField(blank=True, help_text="Open Graph description.")
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True, help_text="Open Graph image.")
    og_url = models.URLField(blank=True, null=True, help_text="Open Graph URL.")
    
    # Twitter Card Metadata
    twitter_title = models.CharField(max_length=255, blank=True, help_text="Twitter Card title.")
    twitter_description = models.TextField(blank=True, help_text="Twitter Card description.")
    twitter_image = models.ImageField(upload_to='seo/', blank=True, null=True, help_text="Twitter Card image.")
    
    # Structured Data (JSON-LD)
    structured_data = JSONField(blank=True, null=True, help_text="JSON-LD structured data.")

    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Metadata for {self.content_object}"

