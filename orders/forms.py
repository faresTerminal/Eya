from django import forms

from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'address_line_1', 'state', 'city', 
            'phone', 'shipping_method', 'pickup_location', 
            'order_note', 'payment_method', 
        ]
   




class AnonymousUserForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    address = forms.CharField(max_length=255)

   