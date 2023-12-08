from django import forms
from .models import ReviewRating, Product, Coupon, Signboard

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

class SignboardForm(forms.ModelForm):
    class Meta:
        model = Signboard
        fields = ['product', 'sub_title', 'big_title', 'price', 'clear_price', 'image_slide']


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))
    


