from django.contrib import admin
from .models import Affiliate, AffiliateReferral, AffiliateCommission, Product

@admin.register(Affiliate)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ('user', 'affiliate_code', 'total_earnings', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'affiliate_code')
    readonly_fields = ('created_at',)

    # Customize the form to display only relevant fields
    fieldsets = (
        (None, {
            'fields': ('user', 'affiliate_code', 'total_earnings', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(AffiliateReferral)
class AffiliateReferralAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'referred_user', 'referral_date')
    list_filter = ('referral_date',)
    search_fields = ('affiliate__user__email', 'referred_user__email')
    readonly_fields = ('referral_date',)

    # Customize the form to display only relevant fields
    fieldsets = (
        (None, {
            'fields': ('affiliate', 'referred_user')
        }),
        ('Timestamps', {
            'fields': ('referral_date',),
            'classes': ('collapse',)
        }),
    )

@admin.register(AffiliateCommission)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'order', 'commission_amount', 'is_paid', 'payment_reference', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('affiliate__user__email', 'order__id')
    readonly_fields = ('created_at',)

    # Customize the form to display only relevant fields
    fieldsets = (
        (None, {
            'fields': ('affiliate', 'order', 'commission_amount','is_paid', 'payment_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
   

