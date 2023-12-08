from django import forms
from .models import Adjustment_StockHistory



class StockAdjustmentForm(forms.ModelForm):

    class Meta:
        model = Adjustment_StockHistory
        fields = ['adjustment_type', 'quantity', 'reason' ]