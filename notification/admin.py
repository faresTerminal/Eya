from django.contrib import admin
from .models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'message', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'message')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        """Customize the queryset to include related user data"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('sender', 'recipient')
        return queryset

admin.site.register(Notification, NotificationAdmin)

