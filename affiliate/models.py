from django.db import models
from accounts.models import Account
from orders.models import Order
from store.models import Product
from django.db.models import Count, Sum

class Affiliate(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='affiliated')
    affiliate_code = models.CharField(max_length=50, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  # Default 10% commission
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.affiliate_code}"

    @property
    def commission_rate(self):
        if self.product:
            return self.product.affiliate_percentage
        return 0.0  # Return 0 if no product is linked

    def pending_commissions(self):
        """Get the total of unpaid (pending) commissions."""
        return AffiliateCommission.objects.filter(affiliate=self, is_paid=False).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0.0

    def withdrawn_commissions(self):
        """Get the total of withdrawn (paid) commissions."""
        return AffiliateCommission.objects.filter(affiliate=self, is_paid=True).aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0.0
        

class AffiliateReferral(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name='referralled')
    referred_user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='referrall')
    referral_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.affiliate.user.email} referred {self.referred_user.email}"

class AffiliateCommission(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)  # Track payment status
    payment_reference = models.CharField(max_length=255, null=True, blank=True)  # Store payment reference from Chargily

    def __str__(self):
        return f"{self.affiliate.user.email} earned {self.commission_amount} from Order #{self.order.id}"


class AffiliateClick(models.Model):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    referral_link = models.CharField(max_length=255)
    source = models.CharField(max_length=100, choices=[
        ('social_media', 'Social Media'),
        ('website', 'Website'),
        ('email', 'Email Marketing'),
        ('other', 'Other')
    ])
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click on {self.referral_link} by {self.affiliate.user.email}"

