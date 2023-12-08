from django.db import models
from category.models import Category, SubCategory
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from tinymce.models import HTMLField

# Create your models here.


class Product(models.Model):
    # Define Product fields here

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
    description     = models.TextField(max_length=500, blank=True)
    images          = models.ImageField(upload_to='photos/products')
    
   
    is_available    = models.BooleanField(default=True)
    is_clearance    = models.BooleanField(default=False)
    category        = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True)
    shipping = models.IntegerField(
        choices=SHIPPING_CHOICES,
        default=0  # Default to Free Shipping
    )
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

    

    def save(self, *args, **kwargs):
        

        if not self.slug:
            self.slug = slugify(self.product_name)

        super().save(*args, **kwargs)

    

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(color='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(size='size', is_active=True)    


class Variation(models.Model):
    product             = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color               = models.CharField(max_length=255, blank = True)
    size                = models.CharField(max_length=255, blank =True)
    price               = models.IntegerField(blank = False)
    clearance_price     = models.IntegerField(blank = True, default=0)
    quantity            = models.PositiveIntegerField(default=0, blank = False)
    initial_stock_quantity = models.PositiveIntegerField(default=0, blank=False)
    reorder_point = models.PositiveIntegerField(default=0, blank=False)
    is_active           = models.BooleanField(default=True)
    created_date        = models.DateTimeField(auto_now=True)


    objects = VariationManager()

    

    def __str__(self):
        return "{} {}".format(self.color, self.size)

    def discount_price(self):
       return self.price - self.clearance_price

    def is_low_stock(self):
        return self.quantity < self.reorder_point

    def stock_difference(self):
        return self.initial_stock_quantity - self.quantity

    

    def valuation(self):
        return self.quantity * self.price

    def Clearance_valuation(self):
        return self.quantity * self.clearance_price


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
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
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


class Daily_slide(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_title = models.CharField(blank = True, max_length=100)
    big_title = models.CharField(blank = True, max_length=100)
    price = models.IntegerField(blank = True)
    clear_price = models.IntegerField(blank = True)
    image_slide = models.ImageField(upload_to='photos/daily_slide')
    description = models.TextField(default="Default Value")
    deal_of_day = models.BooleanField(default=False)
    expiration_time = models.DateTimeField(default=timezone.now() + timezone.timedelta(hours=48))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.big_title

    def is_expired(self):
        return timezone.now() > self.expiration_time

class Signboard(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sub_title = models.CharField(blank = True, max_length=100)
    big_title = models.CharField(blank = True, max_length=100)
    price = models.IntegerField(blank = True)
    clear_price = models.IntegerField(blank = True)
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


