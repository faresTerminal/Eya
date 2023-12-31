from django import forms
from store.models import Product, Variation, ProductGallery, Descriptions

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'description', 'price', 'clearance_price', 'stock', 'is_clearance', 'category', 'subcategory', 'images', 'shipping']
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ['variation_category', 'variation_value', 'is_active']


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = ['image']


class DescriptionForm(forms.ModelForm):
    class Meta:
        model = Descriptions
        fields = ['body', 'additional_info', 'shipping_return']



class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['clearance_price', 'is_clearance']


