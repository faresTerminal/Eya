from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Affiliate, AffiliateReferral, AffiliateCommission, AffiliateClick
from accounts.models import Account
from orders.models import Order
from django.db.models import Sum 
from payment.models import Invoice

@login_required
def become_affiliate(request):
    if request.method == 'POST':
        affiliate_code = request.POST.get('affiliate_code')
        if not Affiliate.objects.filter(affiliate_code=affiliate_code).exists():
            Affiliate.objects.create(
                user=request.user,
                affiliate_code=affiliate_code
            )
            messages.success(request, 'You are now an affiliate!')
            return redirect('affiliate_dashboard')
        else:
            messages.error(request, 'This affiliate code is already taken. Please choose another one.')
    return render(request, 'affiliate/become_affiliate.html')

from django.db.models.functions import TruncDay, TruncMonth
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta
from django.core.paginator import Paginator


@login_required
def affiliate_dashboard(request):
    affiliate = getattr(request.user, 'affiliated', None)
    
    if not affiliate:
        return redirect('become_affiliate')

    # Get affiliate commissions
    commissions = AffiliateCommission.objects.filter(affiliate=affiliate)
    total_earnings = commissions.aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0

    # Get pending commissions (from unpaid orders)
    pending_commissions = commissions.filter(order__status='pending').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    print(pending_commissions)
    # Get withdrawn commissions (assuming 'paid' means withdrawn)
    withdrawn_commissions = commissions.filter(order__status='paid').aggregate(Sum('commission_amount'))['commission_amount__sum'] or 0
    print(withdrawn_commissions)
    # Get referrals
    referrals = AffiliateReferral.objects.filter(affiliate=affiliate)
    total_referrals = AffiliateReferral.objects.filter(affiliate=affiliate).count()

    # Get orders made through this affiliate
    affiliate_orders = Order.objects.filter(purchased_through_affiliate=affiliate)
    total_orders = affiliate_orders.count()

    # Get best-performing products
    best_products = affiliate_orders.values('product__product_name').annotate(
        total_sold=Count('product')
    ).order_by('-total_sold')[:5]  # Top 5 products

    # Get earnings per day (for last 30 days)
    last_30_days = now() - timedelta(days=30)
    daily_earnings = commissions.filter(created_at__gte=last_30_days).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(total=Sum('commission_amount')).order_by('day')

    # Get earnings per month (for last 6 months)
    last_6_months = now() - timedelta(days=180)
    monthly_earnings = commissions.filter(created_at__gte=last_6_months).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(total=Sum('commission_amount')).order_by('month')

    # Pagination for commissions (5 per page)
    paginator = Paginator(commissions, 5)  # 5 commissions per page
    page_number = request.GET.get('page')  # Get the page number from the request
    page_obj = paginator.get_page(page_number)  # Get the current page object

    context = {
        'affiliate': affiliate,
        'referrals': referrals,
        'commissions': page_obj,  # Use the paginated commissions
        'total_earnings': total_earnings,
        'pending_commissions': pending_commissions,
        'withdrawn_commissions': withdrawn_commissions,
        'total_referrals': total_referrals,
        'total_orders': total_orders,
        'best_products': best_products,
        'daily_earnings': list(daily_earnings),
        'monthly_earnings': list(monthly_earnings),
    }
    
    return render(request, 'affiliate/dashboard.html', context)





from django.utils.timezone import now

def track_referral(request, affiliate_code):
    try:
        affiliate = Affiliate.objects.get(affiliate_code=affiliate_code)
        referral_link = request.build_absolute_uri()

        # استنتاج مصدر الزيارة (يمكنك تحسينه لاحقًا)
        source = request.GET.get('source', 'other')

        # تسجيل النقرة
        AffiliateClick.objects.create(
            affiliate=affiliate,
            referral_link=referral_link,
            source=source
        )

        # تخزين كود الإحالة في الكوكيز
        response = redirect('register')
        response.set_cookie('affiliate_code', affiliate_code, max_age=30*24*60*60)  # صالح لمدة 30 يومًا
        return response
    except Affiliate.DoesNotExist:
        messages.error(request, 'Invalid affiliate code.')
        return redirect('register')







from django.contrib.auth.decorators import login_required
from store.models import Product

from django.db.models import Sum, Q



@login_required
def buyer_commission_dashboard(request):
    """ Fetch commissions the buyer (Product owner) needs to pay affiliates """

    # Get all products owned by the logged-in user (buyer)
    buyer_products = Product.objects.filter(buyer=request.user)

    # Get all orders where these products were sold
    commission_payments = AffiliateCommission.objects.filter(order__product__in=buyer_products)

    # Group commissions by affiliate
    affiliates_commissions = {}
    total_due = 0
    total_paid = 0
    total_pending = 0

    for commission in commission_payments:
        affiliate = commission.affiliate
        if affiliate not in affiliates_commissions:
            affiliates_commissions[affiliate] = {
                'total_earnings': 0,
                'total_paid': 0,
                'total_pending': 0,
                'commissions': []
            }
        
        # Total earnings for this affiliate
        affiliates_commissions[affiliate]['total_earnings'] += commission.commission_amount
        
        # Categorize as paid or pending
        if commission.is_paid:
            affiliates_commissions[affiliate]['total_paid'] += commission.commission_amount
            total_paid += commission.commission_amount
        else:
            affiliates_commissions[affiliate]['total_pending'] += commission.commission_amount
            total_pending += commission.commission_amount

        affiliates_commissions[affiliate]['commissions'].append(commission)
        total_due += commission.commission_amount

    # Aggregate commissions per day
    daily_commissions = (
        AffiliateCommission.objects
        .values('created_at')  
        .annotate(total_earnings=Sum('commission_amount'))
        .order_by('created_at')
    )

    daily_commissions_dict = {str(entry['created_at']): entry['total_earnings'] for entry in daily_commissions}

    context = {
        'affiliates_commissions': affiliates_commissions,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'daily_commissions': daily_commissions_dict
    }
    
    return render(request, 'affiliate/buyer_commissions.html', context)


   

from django.core.paginator import Paginator


@login_required
def affiliate_commission_detail(request, affiliate_id):
    """ Show commission details for a specific affiliate """

    affiliate = get_object_or_404(Affiliate, id=affiliate_id)
    
    # Get all commissions this buyer owes to the affiliate
    commission_payments = AffiliateCommission.objects.filter(
        affiliate=affiliate, order__product__buyer=request.user
    )

    # Calculate the total paid commission amount
    total_paid_commission = sum(commission.commission_amount for commission in commission_payments if commission.is_paid)

    # Calculate the total pending commission amount
    total_pending_commission = sum(commission.commission_amount for commission in commission_payments if not commission.is_paid)

    # Calculate the total commission due (pending commissions minus paid commissions)
    total_commission = total_pending_commission + total_paid_commission  # or just use total_pending_commission if that's your requirement

    # Paginate commission payments (show 10 per page)
    paginator = Paginator(commission_payments, 5)  # Show 10 payments per page
    page_number = request.GET.get('page')
    commission_payments_page = paginator.get_page(page_number)

    context = {
        'affiliate': affiliate,
        'commission_payments': commission_payments_page,  # Paginated commissions
        'total_commission': total_commission,
        'total_pending_commission': total_pending_commission,
        'total_paid_commission': total_paid_commission,
    }
    
    return render(request, 'affiliate/commission_detail.html', context)






from django.db.models import Count
from django.utils.timezone import now, timedelta
import json

@login_required
def affiliate_analytics(request):
    affiliate = getattr(request.user, 'affiliated', None)
    if not affiliate:
        return redirect('become_affiliate')

    # 1️⃣ عدد النقرات حسب المصدر
    clicks_by_source = AffiliateClick.objects.filter(affiliate=affiliate)\
        .values('source').annotate(count=Count('id'))

    # 2️⃣ عدد التحويلات لكل منتج
    conversions_by_product = AffiliateCommission.objects.filter(affiliate=affiliate)\
        .values('order__product__product_name').annotate(count=Count('id'))

    # 3️⃣ إيرادات يومية، أسبوعية، وشهرية
    today = now().date()
    daily_earnings = AffiliateCommission.objects.filter(
        affiliate=affiliate, created_at__date=today
    ).aggregate(total=Sum('commission_amount'))['total'] or 0

    weekly_earnings = AffiliateCommission.objects.filter(
        affiliate=affiliate, created_at__date__gte=today - timedelta(days=7)
    ).aggregate(total=Sum('commission_amount'))['total'] or 0

    monthly_earnings = AffiliateCommission.objects.filter(
        affiliate=affiliate, created_at__date__gte=today - timedelta(days=30)
    ).aggregate(total=Sum('commission_amount'))['total'] or 0

    context = {
        'clicks_by_source': json.dumps(list(clicks_by_source)),
        'conversions_by_product': json.dumps(list(conversions_by_product)),
        'daily_earnings': daily_earnings,
        'weekly_earnings': weekly_earnings,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, 'affiliate/analytics.html', context)






def affiliate_payment_success(request, commission_id=None):
    """
    Handle the success of an affiliate commission payment (single or bulk).
    """
    if commission_id:
        # ✅ Case 1: Single commission payment
        commission = get_object_or_404(AffiliateCommission, id=commission_id)

        if not commission.is_paid:
            commission.is_paid = True
            commission.payment_reference = request.GET.get("reference", "CHARGILY_PAYMENT_REFERENCE")  # Dynamic reference
            commission.save()

            # Update affiliate's earnings
            affiliate = commission.affiliate
            affiliate.total_earnings += commission.commission_amount
            affiliate.save()

            # Create an invoice for this payment
            invoice, created = Invoice.objects.get_or_create(
                affiliate=affiliate,
                defaults={
                    'commission_amount': commission.commission_amount,
                    'payment_reference': commission.payment_reference
                }
            )
            if created:
                messages.success(request, f"Invoice created for {affiliate.user.email} for commission {commission.commission_amount} DA")

            messages.success(request, f"Affiliate commission for {affiliate.user.email} has been paid successfully.")

        return render(request, 'affiliate/payment_success.html', {'commission': commission, 'affiliate': affiliate})

    else:
        # ✅ Case 2: Bulk commission payment
        total_amount = request.GET.get("total_amount")
        if total_amount:
            total_amount = float(total_amount)
            
            # Mark all unpaid commissions with this amount as paid
            commissions = AffiliateCommission.objects.filter(is_paid=False, commission_amount__lte=total_amount)

            total_paid = 0
            for commission in commissions:
                commission.is_paid = True
                commission.payment_reference = request.GET.get("reference", "CHARGILY_PAYMENT_REFERENCE")  # Dynamic reference
                commission.save()

                commission.affiliate.total_earnings += commission.commission_amount
                commission.affiliate.save()

                total_paid += commission.commission_amount

            messages.success(request, f"Bulk affiliate payment of {total_paid} DA completed successfully.")

        return render(request, 'affiliate/payment_success.html', {'total_amount': total_amount})

