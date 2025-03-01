# publicite/admin.py

from django.contrib import admin
from .models import Advertisement, SlideAd, ShowAd

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'ad_type', 'is_active', 'start_date', 'end_date', 'impressions')
    list_filter = ('is_active', 'ad_type', 'start_date', 'end_date')
    search_fields = ('title',)
    actions = ['activate_ads', 'deactivate_ads']

    def activate_ads(self, request, queryset):
        queryset.update(is_active=True)

    def deactivate_ads(self, request, queryset):
        queryset.update(is_active=False)

    activate_ads.short_description = "Activate selected ads"
    deactivate_ads.short_description = "Deactivate selected ads"

class SlideAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title',)

class ShowAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title',)

# Remove this line because @admin.register already registers the Advertisement model
# admin.site.register(Advertisement, AdvertisementAdmin)

admin.site.register(SlideAd, SlideAdAdmin)
admin.site.register(ShowAd, ShowAdAdmin)

