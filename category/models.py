from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories', blank=True)
    

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    


    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)

    def get_subcategory_url(self):
        # Ensure that you provide the correct view name and arguments
        return reverse('store_subcategory', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.name