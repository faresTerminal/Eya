from django.contrib import admin
from .models import FacebookPixel

class FacebookPixelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'pixel_id', 'created_at')  # Fields to display in the admin list view
    list_filter = ('user', 'created_at')  # Add filters for better navigation
    search_fields = ('pixel_id', 'user__username')  # Add search functionality
    ordering = ('-created_at',)  # Order items by creation date (newest first)

admin.site.register(FacebookPixel, FacebookPixelAdmin)

