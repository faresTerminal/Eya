from django.db import models
from accounts.models import Account
from django.shortcuts import reverse, Http404

from django.template.defaultfilters import slugify
from django.contrib.postgres.fields import JSONField
from tinymce.models import HTMLField
from django.utils import timezone 

from django.utils.safestring import mark_safe

from django.utils.text import slugify
from django.contrib.auth import get_user_model

# Create your models here.

class Contact(models.Model):
    name = models.CharField(max_length = 50, blank = True, null = True)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length = 50, blank = True, null = True)
    subject = models.CharField(max_length = 50, blank = True, null = True)
    body = models.TextField(max_length = 500, blank = True, null = True)

    def __str__(self):
        return self.subject

class Article(models.Model):
    bloger = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField('title', max_length=9500)
    slug = models.SlugField(max_length=9500, unique_for_date='publish', allow_unicode=True)
    image = models.ImageField('pictur', upload_to = 'Images')
    body = HTMLField()
    featured = models.BooleanField(default=False)
    previous_post = models.ForeignKey(
        'self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey(
        'self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)
    posted_on = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True, auto_now_add=False)
    publish = models.DateTimeField(default=timezone.now) 
   
    def __str__(self):

        return self.title
    
    def get_absolute_url(self):
        return reverse('show_article', kwargs={'id':self.id, 'slug': self.slug})

    def is_featured(self):
        return self.featured

    @property
    def comment_count(self):
        return comment_put.objects.filter(put_to_blog=self).count()

    def save(self, *args, **kwargs):
        

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)
    


class comment_put(models.Model):

    put_to_blog = models.ForeignKey(Article, on_delete = models.CASCADE)
    user_comment = models.ForeignKey(Account, on_delete = models.CASCADE)
    comment = models.TextField(max_length = 500)
    date = models.DateTimeField(auto_now=False, auto_now_add=True)
   
    def __str__(self):
        return self.comment