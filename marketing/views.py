from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Promotion, Coupon, CouponUsage
from django.contrib import messages
from carts.models import CartItem, Cart
from .forms import CouponForm, PromotionForm
from category.models import Category

def get_cart_total(request):
    total = 0
    cart_items = CartItem.objects.filter(
        user=request.user if request.user.is_authenticated else None,
        cart=Cart.objects.get(cart_id=_cart_id(request)) if not request.user.is_authenticated else None,
        is_active=True
    )
    
    for cart_item in cart_items:
        # Check if there are any variations available for the cart item
        variation = cart_item.variations.first()
        if variation:
            # Use clearance_price if available, otherwise use the regular price
            price = variation.clearance_price if variation.clearance_price else variation.price
            total += price * cart_item.quantity
    
    return total




def promotions(request):
    active_promotions = Promotion.objects.filter(is_active=True, start_date__lte=timezone.now(), end_date__gte=timezone.now())
    return render(request, 'marketing/promotions.html', {'promotions': active_promotions})


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)

            # Check if the coupon is valid and the user has not used it before
            if CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                messages.error(request, 'You have already used this coupon before.')
            else:
                total = get_cart_total(request)  # Get the current total of the cart

                # Check if the coupon has reached its maximum usage
                if coupon.used_count >= coupon.max_uses:
                    messages.error(request, 'This coupon has reached its maximum usage limit.')

                # Check if the coupon is valid and the minimum purchase is met
                elif coupon.is_valid() and (coupon.minimum_purchase is None or total >= coupon.minimum_purchase):
                    # Store the coupon in the session for checkout
                    request.session['coupon_code'] = coupon.code
                    coupon.increment_usage()  # Increment the usage count when successfully applied
                    
                    # Track that the user has used this coupon
                    CouponUsage.objects.create(coupon=coupon, user=request.user)
                    
                    messages.success(request, f'Coupon "{coupon.code}" applied successfully!')
                else:
                    messages.error(request, f'The minimum purchase of {coupon.minimum_purchase} DA is required to apply this coupon.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code.')

    return redirect('cart')



from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Coupon
from .forms import CouponForm

@login_required
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        
        # Get the expiration_date from the form data (as a string)
        expiration_date_str = request.POST.get('expiration_date')
        expiration_date = parse_datetime(expiration_date_str)  # Parse the string into a datetime object
        
        # Make sure expiration_date is timezone-aware
        if expiration_date and expiration_date.tzinfo is None:
            expiration_date = timezone.make_aware(expiration_date, timezone.get_current_timezone())
        
        # Now compare expiration_date with timezone.now(), which is aware by default
        if expiration_date and expiration_date <= timezone.now():
            form.add_error('expiration_date', 'The expiration date must be in the future.')
        
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.expiration_date = expiration_date  # Save the aware expiration date
            coupon.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('add_coupon')  # Redirect to a coupon list or success page
        else:
            messages.error(request, 'There was an error creating the coupon.')
    else:
        form = CouponForm()

    return render(request, 'marketing/add_coupon.html', {'form': form})


@login_required
def add_promotion(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST, request.FILES)
        
        # Get the start_date and end_date from the form data
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        
        # Parse the start and end dates from the form
        start_date = parse_datetime(start_date_str)
        end_date = parse_datetime(end_date_str)

        # Make sure the start_date and end_date are timezone-aware
        if start_date and start_date.tzinfo is None:
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
        
        if end_date and end_date.tzinfo is None:
            end_date = timezone.make_aware(end_date, timezone.get_current_timezone())
        
        # Ensure that start_date and end_date are valid (start_date <= end_date)
        if start_date and end_date and start_date >= end_date:
            form.add_error('end_date', 'The end date must be after the start date.')

        if form.is_valid():
            promotion = form.save(commit=False)
            promotion.start_date = start_date  # Save the aware start date
            promotion.end_date = end_date  # Save the aware end date
            promotion.save()
            messages.success(request, 'Promotion created successfully!')
            return redirect('promotion_list')  # Redirect to a promotion list or success page
        else:
            messages.error(request, 'There was an error creating the promotion.')
    else:
        form = PromotionForm()
    categories = Category.objects.all()
    return render(request, 'marketing/add_promotion.html', {'form': form, 'categories': categories})
