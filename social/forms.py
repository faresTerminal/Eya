from django import forms
from .models import FacebookPixel

class FacebookPixelForm(forms.ModelForm):
    class Meta:
        model = FacebookPixel
        fields = ['name', 'pixel_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter pixel name'}),
            'pixel_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Facebook Pixel ID'}),
        }
        labels = {
            'name': 'Pixel Name',
            'pixel_id': 'Facebook Pixel ID',
        }
