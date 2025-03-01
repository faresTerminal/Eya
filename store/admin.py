from .models import Product, Variation,  ReviewRating, Wishlist, ProductGallery, Daily_slide, Signboard, Coupon, Descriptions, Color, Daily_and_Outlet, Signboard_Blog
from django.contrib import admin
import admin_thumbnails

# Register your models here.





@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 4

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'product_type', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]
    

class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']

class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'size', 'price', 'quantity', 'is_active']
    list_filter = ['color', 'product', 'is_active']
    search_fields = ['product__name', 'color__name', 'size']

admin.site.register(Color, ColorAdmin)






    
    


admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(Wishlist)
admin.site.register(ProductGallery)
admin.site.register(Daily_slide)
admin.site.register(Signboard)
admin.site.register(Signboard_Blog)

admin.site.register(Coupon)
admin.site.register(Descriptions)
admin.site.register(Daily_and_Outlet)