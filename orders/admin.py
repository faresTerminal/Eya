from django.contrib import admin
from .models import Order, OrderProduct, City_Region, State, City
# Register your models here.


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'city', 'order_total', 'status', 'is_ordered', 'created_at', 'transaction_id']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'transaction_id']
    list_per_page = 20
    inlines = [OrderProductInline]





admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(City_Region)
admin.site.register(State)
admin.site.register(City)


