from django import forms
from .models import ReviewRating, Product, Coupon, Signboard, Daily_and_Outlet

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']

class SignboardForm(forms.ModelForm):
    class Meta:
        model = Signboard
        fields = ['product', 'sub_title', 'big_title', 'image_slide']


class DealsAndOutletForm(forms.ModelForm):
    expiration_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Daily_and_Outlet
        fields = ['product', 'sub_title', 'image_slide', 'expiration_time', 'deal_of_day']


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))
    


