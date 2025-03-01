

from django.contrib import admin
from .models import SubscriptionPlan, Payment, Invoice, AmountCheckout

# Admin configuration for SubscriptionPlan
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active', 'description')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)

# Admin configuration for Payment
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'gateway', 'payment_date', 'transaction_id', 'payment_link')
    search_fields = ('user__username', 'transaction_id', 'gateway')
    list_filter = ('gateway', 'payment_date')

# Admin configuration for Invoice
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('payment', 'issued_date', 'pdf')
    search_fields = ('payment__transaction_id',)
    list_filter = ('issued_date',)

# Admin configuration for AmountCheckout
class AmountCheckoutAdmin(admin.ModelAdmin):
    list_display = ('amount', 'entity_id', 'payment_method', 'customer', 'status', 'locale', 'created_at', 'checkout_url', 'plan', 'order')
    search_fields = ('entity_id', 'customer__username', 'checkout_url')
    list_filter = ('status', 'payment_method', 'locale', 'created_at')

# Register models with their respective admin configurations
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(AmountCheckout, AmountCheckoutAdmin)


