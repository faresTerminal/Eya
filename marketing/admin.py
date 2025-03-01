from django.contrib import admin
from .models import Promotion, Coupon, CouponUsage

admin.site.register(Promotion)
admin.site.register(CouponUsage)

class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'minimum_purchase', 'is_active', 'expiration_date', 'max_uses', 'used_count')
    search_fields = ('code',)

admin.site.register(Coupon, CouponAdmin)

