from .models import Product, Variation,  ReviewRating, Wishlist, ProductGallery, Daily_slide, Signboard, Coupon, Descriptions
from django.contrib import admin
import admin_thumbnails

# Register your models here.






@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 4

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]
    

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'price', 'is_active')
    list_editable = ('is_active',)
    # filter as product name in admin page
    list_filter = ('product', 'color', 'size', 'price')


    
    


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(Wishlist)
admin.site.register(ProductGallery)
admin.site.register(Daily_slide)
admin.site.register(Signboard)
admin.site.register(Coupon)
admin.site.register(Descriptions)