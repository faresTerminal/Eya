from django.db import models
from category.models import Category, SubCategory
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField
from django.contrib.postgres.fields import JSONField

from colorfield.fields import ColorField

# Create your models here.


class Product(models.Model):
    # Define Product fields here
    PHYSICAL = 'physical'
    DIGITAL = 'digital'

    PRODUCT_TYPE_CHOICES = [
        (PHYSICAL, 'Physical'),
        (DIGITAL, 'Digital'),
    ]


    # Define choices for the shipping field
    SHIPPING_CHOICES = (
        
        (200, '200 DA'),
        (300, '300 DA'),
        (400, '400 DA'),
        (500, '500 DA'),
        (600, '600 DA'),
        (0, 'Free Shipping (0 DA)'),
        # Add more options as needed
    )
   
    buyer           = models.ForeignKey(Account, on_delete=models.CASCADE)
    product_name    = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=200, unique=True)
    description     = HTMLField()
    images          = models.ImageField(upload_to='photos/products')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    is_available    = models.BooleanField(default=True)
    is_clearance    = models.BooleanField(default=False)
    category        = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    shipping = models.DecimalField(max_digits=10, decimal_places=2,
        choices=SHIPPING_CHOICES,
        default=0  # Default to Free Shipping
    )
    product_type = models.CharField(
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default=PHYSICAL
    )
    digital_file = models.FileField(upload_to='files/products/digital_files', blank=True, null=True)
    is_affiliate_enabled = models.BooleanField(default=False)  
    affiliate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, null=True)  
    # Existing fields...
    trial_start_date = models.DateTimeField(auto_now_add=True)
    trial_active = models.BooleanField(default=True)

    
    featured = models.BooleanField(default=False)
    previous_product = models.ForeignKey(
        'self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_product = models.ForeignKey(
        'self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)
    created_date    = models.DateTimeField(auto_now_add=True)
    modified_date   = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

   

    def get_subcategory_url(self):
        # Ensure that you provide the correct view name and arguments
        return reverse('store_subcategory', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def has_more_than_20_reviews(self):
        review_count = self.countReview()
        return review_count > 20

    def is_clearance_product(self):
        return self.is_clearance

    def is_new_product(self):
        now = timezone.now()
        days_since_creation = (now - self.created_date).days
        return days_since_creation <= 5

    

    def save(self, *args, **kwargs):
        

        if not self.slug:
            self.slug = slugify(self.product_name)

        super().save(*args, **kwargs)


    def trial_expiration_date(self):
        return self.trial_start_date + timedelta(days=90)
        

    def is_trial_active(self):
        return self.trial_active and now() < self.trial_expiration_date()

    def get_file_extension(self):
        if self.digital_file:
            return self.digital_file.name.split('.')[-1]  # Get the extension of the file
        return None

    

class Color(models.Model):
    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7)  # To store the hex color code (e.g., #FF0000)

    def __str__(self):
        return self.name   

class VariationManager(models.Manager):
    

    def sizes(self):
        return super(VariationManager, self).filter(size='size', is_active=True)    


class Variation(models.Model):
    VARIANT_TYPE_CHOICES = (
        ('no_variant', 'No Variant'),
        ('color', 'Color Only'),
        ('size', 'Size Only'),
        ('size_and_color', 'Color and Size'),
    )
   
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True) 
    size = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    clearance_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.0)
    quantity = models.PositiveIntegerField(default=0, blank=False)
    initial_stock_quantity = models.PositiveIntegerField(default=0, blank=False)
    reorder_point = models.PositiveIntegerField(default=0, blank=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    # New field to specify the variant type
    variant_type = models.CharField(
    max_length=255, 
    choices=VARIANT_TYPE_CHOICES, 
    default='no_variant',
    blank=False  # This ensures the field cannot be left empty
    )

    objects = VariationManager()

    def __str__(self):
        return "{} - {} - {} {}".format(
            self.product.product_name,  # Assuming your Product model has a 'product_name' field
            self.variant_type,          # Variant type ('color', 'size', etc.)
            "Price:", self.price        # Displaying the price
        )

    def discount_price(self):
        if self.clearance_price and self.clearance_price > 0:
                return self.price - self.clearance_price
        return self.price  # Return the original price if no discount

    def is_low_stock(self):
        return self.quantity < self.reorder_point

    def stock_difference(self):
        return self.initial_stock_quantity - self.quantity

    def valuation(self):
        return self.quantity * self.price

    def clearance_valuation(self):
        return self.quantity * self.clearance_price

    # Override save method
    def save(self, *args, **kwargs):
        # If quantity is set, make initial_stock_quantity equal to quantity
        if self.quantity is not None and self.initial_stock_quantity == 0:
            self.initial_stock_quantity = self.quantity
        super().save(*args, **kwargs)



class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject



class Wishlist(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name





class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, related_name='galleries')
    image = models.ImageField(upload_to='store/products', max_length=255, null=True, blank=True)
    youtube_url = models.URLField(blank=True, null=True, help_text="YouTube video URL (optional)")

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'product gallery'
        verbose_name_plural = 'product galleries'





class Daily_slide(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="daily_slides")
    sub_title = models.CharField(blank=True, max_length=100)
    image_slide = models.ImageField(upload_to='photos/daily_slide')
    description = models.TextField(default="Default Value")
    deal_of_day = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_title

    def is_expired(self):
        return timezone.now() > self.expiration_time


class Daily_and_Outlet(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
   
    sub_title = models.CharField(blank = True, max_length=100)
   
   
    image_slide = models.ImageField(upload_to='photos/deals-and-outlet')
    description = models.TextField(default="Default Value")
    deal_of_day = models.BooleanField(default=False)
    expiration_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sub_title

    def is_expired(self):
        return timezone.now() > self.expiration_time

class Signboard(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_title = models.CharField(blank = True, max_length=100)
    big_title = models.CharField(blank = True, max_length=100)
   
    image_slide= models.ImageField(upload_to='photos/signboard')

    def __str__(self):
        return self.big_title

   

class Coupon(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)
    discount = models.FloatField(blank=True, default=0)
   
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Descriptions(models.Model):
    product         = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='descriptions')
    body            = HTMLField()
    additional_info = HTMLField()
    shipping_return = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
   
    

    def __str__(self):
        # Split the 'body' content into words
        words = self.additional_info.split()
        
        # Take the first 5 words and join them back into a string
        first_5_words = ' '.join(words[:5])

        return first_5_words




class Signboard_Blog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_title = models.CharField(blank = True, max_length=100)
    big_title = models.CharField(blank = True, max_length=100)
    price = models.IntegerField(blank = True)
    clear_price = models.IntegerField(blank = True)
    image_slide= models.ImageField(upload_to='photos/blog_signboard')

    def __str__(self):
        return self.big_title

    @property
    def reward_percentage(self):
        if self.price and self.clear_price:
            # Calculate the reward percentage
            return ((self.price - self.clear_price) / self.price) * 100
        return None







