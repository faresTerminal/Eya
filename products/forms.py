from django import forms
from store.models import Product, Variation, ProductGallery, Descriptions


from tinymce.widgets import TinyMCE  # Import TinyMCE widget


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'is_clearance', 'category', 'subcategory', 'product_type', 'images', 'shipping', 'cost_price', 'is_affiliate_enabled', 'affiliate_percentage', 'digital_file']

        # You can customize the widget for product_type if needed
    product_type = forms.ChoiceField(choices=Product.PRODUCT_TYPE_CHOICES, widget=forms.Select())


    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Set class for all fields for consistent styling
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Set TinyMCE widget for the 'description' field
        self.fields['description'].widget = TinyMCE(attrs={'class': 'form-control', 'cols': 80, 'rows': 30})



    

class VariantForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['variant_type', 'color', 'size', 'price', 'quantity', 'is_active']

    


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = ['image', 'youtube_url']


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Descriptions
        fields = ['body', 'additional_info', 'shipping_return']



class VariationtUpdateForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['clearance_price']


