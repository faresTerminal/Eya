from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import string
from django.utils.timezone import now, timedelta
from django.utils import timezone

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name      = models.CharField(max_length=50)
    last_name       = models.CharField(max_length=50)
    username        = models.CharField(max_length=50, unique=True)
    email           = models.EmailField(max_length=100, unique=True)
    

    # required
    date_joined     = models.DateTimeField(auto_now_add=True)
    last_login      = models.DateTimeField(auto_now_add=True)
    is_admin        = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=False)
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    referred_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='referralled'  # Unique related_name
    )
    is_superadmin        = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_trial = models.BooleanField(default=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    subscription_active = models.BooleanField(default=False)
    subscription_expiry_date = models.DateTimeField(null=True, blank=True)
    confirmation_code_sent_at = models.DateTimeField(null=True, blank=True)
    confirmation_code = models.CharField(max_length=6, blank=True, null=True)  # Adjust length as needed
    is_confirmed = models.BooleanField(default=False)  # To track whether the account is confirmed

    # Other methods...
    
    def generate_confirmation_code(self):
        """Generate a random confirmation code."""
        code = ''.join(random.choices(string.digits, k=6))  # You can adjust the length of the code
        self.confirmation_code = code
        self.save()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True

    def is_trial_valid(self):
       """Check if the trial period is still valid."""
       return self.is_trial and self.trial_end_date > timezone.now()


    def is_subscription_valid(self):
        """Check if the user has a valid active subscription."""
        return self.subscription_active and self.subscription_expiry_date > timezone.now()


 #for website       
class Shop_Social(models.Model):
    title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200)
    facebook = models.URLField(blank = True)
    instagram = models.URLField(blank = True)
    youtube = models.URLField(blank = True)
    twiter = models.URLField(blank = True)
    pinterest= models.URLField(blank = True)
    tiktok = models.URLField(blank = True)

    def __str__(self):
        return self.title

#for Etch User      
class Shop_Social_User(models.Model):
    user_social = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    facebook = models.URLField(blank = True)
    instagram = models.URLField(blank = True)
    youtube = models.URLField(blank = True)
    twiter = models.URLField(blank = True)
    pinterest= models.URLField(blank = True)
    tiktok = models.URLField(blank = True)

    def __str__(self):
        return self.title
		

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete = models.CASCADE)
    shop_social = models.OneToOneField(Shop_Social_User, on_delete=models.SET_NULL, null=True, blank=True)
    address_line1 = models.CharField(max_length = 100, blank= True)
    address_line2 = models.CharField(max_length = 100, blank= True)
    profile_picture = models.ImageField(blank = True, upload_to = 'userprofile')
    city = models.CharField(blank = True, max_length = 50)
    state = models.CharField(blank = True, max_length = 50)
    country = models.CharField(blank = True, max_length = 50)
    show_email = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name

    def full_adress(self):
        return f'(self.address_line1) (self.address_line2)'







class SellerReview(models.Model):
    seller = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='seller_reviews')
    reviewer = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='buyer_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # Rating out of 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.reviewer.username} for {self.seller.username}'




