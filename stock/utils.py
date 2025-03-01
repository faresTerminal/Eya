# inventory_app/utils.py

from .models import Product, StockHistory

def log_stock_change(product, user, quantity_before_change, quantity_after_change, reason_for_change):
    StockHistory.objects.create(
        product=product,
        user=user,
        quantity_before_change=quantity_before_change,
        quantity_after_change=quantity_after_change,
        reason_for_change=reason_for_change,
    )
