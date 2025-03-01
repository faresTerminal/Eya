from django.contrib import admin
from .models import StockHistory, Adjustment_StockHistory
# Register your models here.
admin.site.register(StockHistory)
admin.site.register(Adjustment_StockHistory)