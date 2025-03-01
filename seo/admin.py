from django.contrib import admin
from .models import Metadata

@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'title', 'canonical_url', 'updated_at')
    list_filter = ('content_type',)
    search_fields = ('title', 'description', 'keywords', 'og_title', 'twitter_title')
    fieldsets = (
        ("SEO Metadata", {
            "fields": ('title', 'description', 'keywords', 'canonical_url')
        }),
        ("Open Graph Metadata", {
            "fields": ('og_title', 'og_description', 'og_image', 'og_url')
        }),
        ("Twitter Card Metadata", {
            "fields": ('twitter_title', 'twitter_description', 'twitter_image')
        }),
        ("Structured Data", {
            "fields": ('structured_data',)
        }),
    )


