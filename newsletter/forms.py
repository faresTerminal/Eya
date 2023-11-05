from django import forms
from .models import EmailSubscription

class EmailSubscriptionForm(forms.ModelForm):
    class Meta:
        model = EmailSubscription
        fields = ['email']


    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add custom validation logic if needed
        return email