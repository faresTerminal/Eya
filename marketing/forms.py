from django import forms
from .models import Coupon
from .models import Promotion
from django.utils import timezone
from category.models import Category


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'minimum_purchase', 'expiration_date', 'max_uses', 'is_active', 'used_count']
        widgets = {
            'expiration_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_code(self):
        # Ensure coupon code is unique
        code = self.cleaned_data.get('code')
        if Coupon.objects.filter(code=code).exists():
            raise forms.ValidationError("This coupon code already exists.")
        return code






class PromotionForm(forms.ModelForm):
    # Fields that are automatically created based on the model
    class Meta:
        model = Promotion
        fields = ['title', 'categories', 'image_background', 'description', 'discount_percentage', 'start_date', 'end_date', 'is_active']
        
        # You can add widgets for any fields if needed. For example, for start_date and end_date, you can set the widget to "datetime-local"
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_end_date(self):
        """
        Ensure that end_date is after start_date
        """
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('End date must be after the start date.')
        return end_date

    def clean_start_date(self):
        """
        Ensure that start_date is in the future (can't create promotions that start in the past).
        """
        start_date = self.cleaned_data.get('start_date')
        
        if start_date and start_date <= timezone.now():
            raise forms.ValidationError('Start date must be in the future.')
        return start_date