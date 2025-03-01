from django import forms
from .models import Account, UserProfile, SellerReview, Shop_Social_User
from phonenumbers import parse, is_valid_number, NumberParseException

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class': 'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password'
    }))
    affiliate_code = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Affiliate Code (Optional)',
        'class': 'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password', 'affiliate_code']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


    



   

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line1', 'address_line2', 'city', 'state', 'country', 'profile_picture', 'show_email')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'





class SellerReviewForm(forms.ModelForm):
    class Meta:
        model = SellerReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
        }


class UserSocialForm(forms.ModelForm):
    class Meta:
        model = Shop_Social_User
        fields = ('title', 'facebook', 'instagram', 'youtube', 'twiter', 'pinterest', 'tiktok')