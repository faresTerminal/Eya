
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from .forms import StockAdjustmentForm
from store.models import Product, Variation
from django.db.models import F
from stock.utils import log_stock_change
from stock.models import StockHistory, Adjustment_StockHistory
from django.utils import timezone
from django.db.models import Avg, Sum
from orders.models import OrderProduct
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


# Create your views here.
def stock(request):
    products = Product.objects.filter(buyer=request.user, is_available=True).order_by('-id')[:3]
    total_products = Product.objects.filter(buyer=request.user, is_available=True).count()

    # Fetch low stock variations directly
    low_stock_variations = Variation.objects.filter(product__buyer=request.user, quantity__lt=15).order_by('-id')[:4]

    # Calculate average stock quantity
    total_stock = Variation.objects.filter(product__in=products).aggregate(total_stock=Sum('quantity'))
    total_stock = total_stock['total_stock'] if total_stock['total_stock'] else 0
    average_stock = total_stock / max(len(products), 1)

    context = {
        'products': products,
        'total_products': total_products,
        'low_stock_variations': low_stock_variations,
        'average_stock': average_stock,
    }
    return render(request, 'stock/index.html', context)

def product_list_stock(request):
    products = Product.objects.filter(buyer = request.user, is_available = True)
    variation_list = Variation.objects.filter(product__in = products)

    paginator = Paginator(variation_list, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = variation_list.count()



    context = {
	'products': products,
    'variation_list': paged_products,

    }
    return render(request, 'stock/product_list_stock.html', context)



def stock_adjust_page(request):
    products = Product.objects.filter(buyer = request.user, is_available = True)
    variation_list = Variation.objects.filter(product__in = products)

    paginator = Paginator(variation_list, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = variation_list.count()

    context = {
	'products': products,
    'variation_list': paged_products,

    }
    return render(request, 'stock/stock_adjustment.html', context)

def stock_adjustment(request, product_id):
    product = Variation.objects.get(pk=product_id)

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            adjustment_type = form.cleaned_data['adjustment_type']

            if adjustment_type == 'add':
                product.quantity += quantity
            elif adjustment_type == 'subtract':
                product.quantity = max(product.quantity - quantity, 0)

            product.save()
            # Record the stock adjustment in the stock history
            Adjustment_StockHistory.objects.create(
                product=product,
                adjusted_by=request.user,  # Assuming you have user authentication
                adjustment_type=adjustment_type,
                quantity=quantity,
                timestamp=timezone.now(),
                reason=form.cleaned_data['reason'],  # Add a 'reason' field to your form
            )
            return redirect('product_list_stock')  # Redirect to your product list view

    else:
        form = StockAdjustmentForm()

    context = {
        'product': product,
        'form': form,
    }

    return render(request, 'stock/stock_update_adjust.html', context)

from notification.models import Notification



from django.db.models import F

def low_stock(request):
    # Filter products associated with the logged-in buyer
    products = Product.objects.filter(buyer=request.user, is_available=True)

    # Find variations where stock is lower than reorder_point
    low_stock_products = Variation.objects.filter(product__in=products, quantity__lt=F('reorder_point'))

    for variation in low_stock_products:
        # Calculate reorder_point and reorder_point/2
        reorder_point = variation.reorder_point
        reorder_half = reorder_point / 2
        quantity = variation.quantity
        
        # Check if the reorder point or reorder half point has been crossed and no previous notification exists
        if quantity == reorder_point and not Notification.objects.filter(
            sender=request.user,
            recipient=request.user,
            message__icontains=f"Product (Low Stock): {variation.product.product_name}",
            url=f"/stock/low_stock/"
        ).exists():
            # Send notification for reorder point
            Notification.objects.create(
                sender=request.user,
                recipient=request.user,
                message=f"Product (Low Stock): {variation.product.product_name}\nReorder Point reached.",
                url=f"/stock/low_stock/",
                profile_picture_url=variation.product.images.url if variation.product.images else None
            )
        
        

    context = {
        'low_stock_products': low_stock_products,
    }
    return render(request, 'stock/low_stock.html', context)




def stock_valuation(request):
    products = Product.objects.filter(buyer = request.user, is_available = True)
    variation_valuation = Variation.objects.filter(product__in = products)
    total_valuation = sum(product.valuation() for product in variation_valuation)

    context = {
        'products': products,
        'variation_valuation': variation_valuation,
        'total_valuation': total_valuation,
    }

    return render(request, 'stock/stock_valuation.html', context)



# update stock to see history stock opiration
def update_stock(request, product_id):
    product = Variation.objects.get(pk=product_id)

    if request.method == 'POST':
        quantity_before_change = product.quantity
        new_quantity = int(request.POST['new_quantity'])
        product.quantity = new_quantity
        product.save()

        # Log the stock change
        log_stock_change(
            product=product,
            user=request.user,
            quantity_before_change=quantity_before_change,
            quantity_after_change=new_quantity,
            reason_for_change=request.POST.get('reason_for_change', ''),
        )

        return redirect('product_list_stock')

    context = {
        'product': product,
    }

    return render(request, 'stock/update_stock.html', context)



def stock_history(request):
    #user = Product.objects.filter(buyer = request.user, is_available = True)
    adjustment_stock_history = Adjustment_StockHistory.objects.filter(adjusted_by = request.user).order_by('-timestamp')
    stock_history = StockHistory.objects.filter(user = request.user).order_by('-change_date')

    context = {
        
        'stock_history': stock_history,
        'adjustment_stock_history': adjustment_stock_history,
    }

    return render(request, 'stock/stock_history.html', context)




