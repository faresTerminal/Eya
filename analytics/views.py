

# analytics/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import PageView, OrderAnalytics
from django.db.models import Sum, Count
from store.models import Product, Variation, ReviewRating
from orders.models import Order, OrderProduct
from accounts.models import Account, UserProfile
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware


def customer_sales_analysis(user):
    # Filter orders for products owned by the main customer (seller)
    aggregated_data = (
        OrderProduct.objects.filter(product__buyer=user, ordered=True)  # Filter by seller's products
        .values('user')  # Group by purchasing user
        .annotate(
            total_spent=Sum(F('product_price') * F('quantity'), output_field=DecimalField())  # Calculate total spending
        )
    )

    customer_data = []

    for data in aggregated_data:
        try:
            # Get purchasing user's account and profile
            customer = Account.objects.get(id=data['user'])
            user_profile = UserProfile.objects.get(user=customer)
        except ObjectDoesNotExist:
            customer = None
            user_profile = None

        customer_data.append({
            'user': customer,
            'total_spent': data['total_spent'] or 0.0,
            'profile_picture': user_profile.profile_picture.url if user_profile and user_profile.profile_picture else None,
            'email': customer.email if customer else None,
            'username': customer.username if customer else None,
        })

    return customer_data


def analyze_transactions(user):
    """
    Analyze transactions for each product owned by the user:
    - total_deposits: Cost price without multiplying by quantity.
    - total_deposits_with_quantity: Cost price multiplied by quantity in orders.
    - total_withdrawals: Cumulative profit from orders.
    """
    products = Product.objects.filter(buyer=user)  # Products created by the user

    analysis = []

    for product in products:
        # Cost price (without quantity)
        cost_price = product.cost_price or Decimal('0.00')

        # Total Deposits (cost_price * quantity)
        total_deposits_with_quantity = OrderProduct.objects.filter(
            product=product, ordered=True
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('product__cost_price') * F('quantity'),
                    output_field=DecimalField()
                )
            )
        )['total'] or Decimal('0.00')

        # Total Withdrawals (Sum((product_price - cost_price) * quantity))
        total_withdrawals = OrderProduct.objects.filter(
            product=product, ordered=True
        ).aggregate(
            total=Sum(
                ExpressionWrapper(
                    F('product_price') * F('quantity'),
                    output_field=DecimalField()
                )
            )
        )['total'] or Decimal('0.00')

        # Total Quantity Sold
        total_quantity = OrderProduct.objects.filter(
            product=product, ordered=True
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        # Balance (Total Profit)
        balance = total_withdrawals - total_deposits_with_quantity

        analysis.append({
            'product': product,
            'cost_price': cost_price,  # Base cost price (no quantity)
            'total_deposits_with_quantity': total_deposits_with_quantity,  # Cost price * quantity
            'total_withdrawals': total_withdrawals,
            'balance': balance,
            'quantity': total_quantity,
        })

    return analysis




from datetime import datetime

from django.utils.timezone import make_aware



def total_profit_view(user):
    """
    Calculate the total profit for products sold by a specific buyer.
    """
    # Calculate Total Revenue from sold products
    total_revenue = OrderProduct.objects.filter(
        product__buyer=user, ordered=True
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('product_price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or Decimal('0.0')  # Ensure Decimal, not float

    # Calculate Total Cost for sold products
    total_cost = OrderProduct.objects.filter(
        product__buyer=user, ordered=True
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('product__cost_price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or Decimal('0.0')  # Ensure Decimal, not float

    # Calculate Profit
    total_profit = total_revenue - total_cost

    return {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_profit': total_profit,
    }

def get_daily_overview(user):
    today = now().date()  # Get today's date
    yesterday = today - timedelta(days=1)  # Get yesterday's date

    # Sales for the current day (today)
    current_day_sales = OrderProduct.objects.filter(
        product__buyer=user,
        ordered=True,
        created_at__date=today,  # Only for today's date
    ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

    # Sales for the previous day (yesterday)
    previous_day_sales = OrderProduct.objects.filter(
        product__buyer=user,
        ordered=True,
        created_at__date=yesterday,  # Only for yesterday's date
    ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

    # Calculate performance comparison
    if previous_day_sales > Decimal('0.00'):
        performance = ((current_day_sales - previous_day_sales) / previous_day_sales) * Decimal('100.00')
    else:
        performance = 100.0 if current_day_sales > Decimal('0.00') else 0.0

    return {
        'current_day_sales': current_day_sales,
        'previous_day_sales': previous_day_sales,
        'performance': round(performance, 2),  # Round performance to 2 decimal places
    }

# Get current and previous week dates
def get_weekly_overview(user):

    today = now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday this week
    start_of_last_week = start_of_week - timedelta(weeks=1)  # Monday last week
    end_of_last_week = start_of_week - timedelta(days=1)     # Sunday last week

    # Sales for the current week
    current_week_sales = OrderProduct.objects.filter(
        product__buyer=user,
        ordered=True,
        created_at__date__gte=start_of_week,
    ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

    # Sales for the previous week
    previous_week_sales = OrderProduct.objects.filter(
        product__buyer=user,
        ordered=True,
        created_at__date__range=(start_of_last_week, end_of_last_week),
    ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

    # Calculate performance comparison
    if previous_week_sales > 0:
        performance = ((current_week_sales - previous_week_sales) / previous_week_sales) * 100
    else:
        performance = 100.0 if current_week_sales > 0 else 0.0

    return {
        'current_week_sales': current_week_sales,
        'previous_week_sales': previous_week_sales,
        'performance': performance,
    }

    

def get_monthly_growth(user):
    # Get the current date
    today = now().date()
    first_day_of_current_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)

    # Current month sales/revenue
    current_month_revenue = OrderProduct.objects.filter(
        product__buyer=user,  # Filter by the user (optional, if relevant)
        created_at__gte=first_day_of_current_month,  # From the 1st of this month
    ).aggregate(
        total_revenue=Sum(
            F('product_price') * F('quantity'),
            output_field=DecimalField()  # Explicitly set the output field to DecimalField
        )
    )['total_revenue'] or Decimal('0.0')  # Make sure fallback is a Decimal

    # Previous month sales/revenue
    previous_month_revenue = OrderProduct.objects.filter(
        product__buyer=user,  # Filter by the user (optional, if relevant)
        created_at__gte=first_day_of_previous_month,
        created_at__lt=first_day_of_current_month,
    ).aggregate(
        total_revenue=Sum(
            F('product_price') * F('quantity'),
            output_field=DecimalField()  # Explicitly set the output field to DecimalField
        )
    )['total_revenue'] or Decimal('0.0')  # Make sure fallback is a Decimal

    # Calculate growth
    if previous_month_revenue > Decimal('0.0'):  # Compare with Decimal
        growth_percentage = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * Decimal('100.0')
    else:
        growth_percentage = Decimal('0.0')  # Avoid division by zero

    return {
        'current_month_revenue': current_month_revenue,
        'previous_month_revenue': previous_month_revenue,
        'growth_percentage': round(growth_percentage, 2),
    }



def DashboardAnalytics(request):
    user = request.user
    today = make_aware(datetime.today().replace(hour=0, minute=0, second=0, microsecond=0))  # Start of today
    product = Product.objects.filter(buyer=user, is_available=True)
    total_revenue = OrderAnalytics.objects.filter(completed=True, product__buyer = user).aggregate(Sum('total_value'))['total_value__sum'] or 0
    # Count of completed sales
    # Total revenue for today (completed orders from today)
    total_revenue_today = OrderAnalytics.objects.filter(
        completed=True, 
        product__buyer=user,
        created_at__date=today  # Ensure the order was created today or after
    ).aggregate(Sum('total_value'))['total_value__sum'] or 0


    sales_count = OrderAnalytics.objects.filter(completed=True, product__in = product).count()

    # Total unique customers count
    customers_count = Order.objects.filter(is_ordered=True, product__in = product).values('user').distinct().count()

     # Count products sold (sum of quantities in OrderProduct for completed orders)
    products_sold_count = OrderProduct.objects.filter(order__status='Completed', product__in = product).aggregate(Sum('quantity'))['quantity__sum'] or 0
    shippint_revenue_total = OrderAnalytics.objects.filter(completed=True, product__buyer = user).aggregate(Sum('shipping_cost'))['shipping_cost__sum'] or 0

    most_viewed_products = Product.objects.filter(buyer=user).annotate(view_count=Count('productview')).filter(view_count__gt=0).order_by('-view_count')[:3]
    growth_data = get_monthly_growth(user)
    daily_overview = get_daily_overview(user)
    weekly_overview_data = get_weekly_overview(user)
    total_profit = total_profit_view(user)
    analytics_data = analyze_transactions(user)
    # Sort and limit the data
    analytics_data = sorted(analytics_data, key=lambda x: x['total_withdrawals'], reverse=True)[:3]

    customer_data = customer_sales_analysis(user)
    customer_data = sorted(customer_data, key=lambda x: x['total_spent'], reverse=True)[:3]
    

   # Query total earnings for products created by the user (buyer)
    total_earnings = OrderProduct.objects.filter(
         product__buyer=user,  # Ensure this filters orders linked to the user's products
         ordered=True  # Include only completed orders
    ).aggregate(
    total_earnings=Sum(
        F('product_price') * F('quantity'),
        output_field=DecimalField()  # Explicitly set the output field to DecimalField
    )
    )['total_earnings'] or 0.0



     # Aggregate total sales by state
    sales_by_state_data = Order.objects.filter(product__buyer=user).values('state').annotate(
        total_sales=Sum(F('orderproduct__product_price') * F('orderproduct__quantity'), output_field=DecimalField())
    ).order_by('-total_sales')  # Optionally order by total sales in descending order
    

    
    
    context = {
        'total_revenue': total_revenue,
        'most_viewed_products': most_viewed_products,
        'sales_count': sales_count,
        'customers_count': customers_count,
        'products_sold_count': products_sold_count,
        'growth_data': growth_data,
        'total_earnings': total_earnings,
        'weekly_overview_data': weekly_overview_data,
        'total_profit': total_profit,
        'analytics_data': analytics_data,
        'customer_data': customer_data,
        'state_data': sales_by_state_data,
        'shippint_revenue_total': shippint_revenue_total,
        'total_revenue_today': total_revenue_today,
        'daily_overview': daily_overview,
       
    }
    
    return render(request, 'analytics/dashboard.html', context)


def Product_Viewer(request):
    user = request.user
    product = Product.objects.filter(buyer = user)

    most_viewed_products = Product.objects.filter(buyer=user).annotate(view_count=Count('productview')).filter(view_count__gt=0).order_by('-view_count')

    context = {
     'most_viewed_products': most_viewed_products,
    }
    return render(request, 'analytics/product_viewer.html', context)





""" Product Profits """
def Product_Profits(request):

    user = request.user
    analytics_data = analyze_transactions(user)
    # Sort and limit the data
    analytics_data = sorted(analytics_data, key=lambda x: x['total_withdrawals'], reverse=True)
    context = {
     'analytics_data': analytics_data,
    }
    return render(request, 'analytics/product_profits.html', context)



def get_weekly_sales_data_for_product(product):
    """
    Get weekly sales data for a specific product, from Sunday to Saturday for both the current and previous week.
    """
    today = now().date()  # Get today's date
    sunday = today - timedelta(days=today.weekday())  # Sunday this week
    days_of_week = [sunday + timedelta(days=i) for i in range(7)]  # Sunday to Saturday

    # Calculate the start of the previous week (Sunday to Saturday)
    start_of_last_week = sunday - timedelta(weeks=1)
    days_of_last_week = [start_of_last_week + timedelta(days=i) for i in range(7)]

    # Prepare dictionaries to store sales data for both current and previous week
    current_week_sales = {}
    previous_week_sales = {}

    # Fetch sales data for current and previous week
    for i, day in enumerate(days_of_week):
        current_day_sales = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__date=day,
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')
        
        previous_day_sales = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__date=days_of_last_week[i],
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

        current_week_sales[day.strftime('%A')] = current_day_sales
        previous_week_sales[days_of_last_week[i].strftime('%A')] = previous_day_sales

    return {
        'current_week_sales': current_week_sales,
        'previous_week_sales': previous_week_sales
    }


def get_monthly_sales_data_for_product(product):
    """
    Get monthly sales data for a specific product, from January to December for both the current and previous year.
    """
    today = now().date()  # Get today's date
    current_year = today.year  # Get the current year
    previous_year = current_year - 1  # Get the previous year

    months_of_year = [f"{month:02d}" for month in range(1, 13)]  # Month format '01', '02', ..., '12'

    # Prepare dictionaries to store sales data for both current and previous year
    current_year_sales = {}
    previous_year_sales = {}

    # Fetch sales data for current and previous year
    for month in months_of_year:
        # Current year sales data
        current_month_sales = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__year=current_year,
            created_at__month=int(month),
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')
        
        # Previous year sales data
        previous_month_sales = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__year=previous_year,
            created_at__month=int(month),
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

        current_year_sales[month] = current_month_sales
        previous_year_sales[month] = previous_month_sales

    return {
        'current_year_sales': current_year_sales,
        'previous_year_sales': previous_year_sales
    }




def get_weekly_sales_data_for_product_per_month(product):
    """
    Get weekly sales data (for 4 weeks) for a specific product, for both the current and previous month.
    """
    today = now().date()  # Get today's date
    current_year = today.year  # Get the current year
    current_month = today.month  # Get the current month

    # Calculate the start date of the current month
    first_day_of_current_month = today.replace(day=1)
    last_day_of_current_month = (first_day_of_current_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # Calculate the start and end dates for the previous month
    first_day_of_previous_month = (first_day_of_current_month - timedelta(days=1)).replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)

    # Prepare lists to store sales data for both current and previous month
    current_month_sales = []
    previous_month_sales = []

    # Calculate weekly sales for both current and previous month
    for i in range(4):
        # For current month, calculate the week start and end dates
        start_of_current_week = first_day_of_current_month + timedelta(weeks=i)
        end_of_current_week = min(start_of_current_week + timedelta(days=6), last_day_of_current_month)

        # For previous month, calculate the week start and end dates
        start_of_previous_week = first_day_of_previous_month + timedelta(weeks=i)
        end_of_previous_week = min(start_of_previous_week + timedelta(days=6), last_day_of_previous_month)

        # Current month sales for the week
        current_week_sales_value = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__date__gte=start_of_current_week,
            created_at__date__lte=end_of_current_week,
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

        # Previous month sales for the week
        previous_week_sales_value = OrderProduct.objects.filter(
            product=product,
            ordered=True,
            created_at__date__gte=start_of_previous_week,
            created_at__date__lte=end_of_previous_week,
        ).aggregate(
            total=Sum(F('product_price') * F('quantity'), output_field=DecimalField())
        )['total'] or Decimal('0.00')

        # Append the sales data to the lists
        current_month_sales.append(current_week_sales_value)
        previous_month_sales.append(previous_week_sales_value)

    return {
        'current_month_sales': current_month_sales,
        'previous_month_sales': previous_month_sales
    }


from collections import defaultdict



def get_sales_by_region_for_product(product):
    """
    Get sales by region (wilaya_name) for a specific product.
    Returns a dictionary of regions (wilaya_name) and total sales for each region.
    """
    # Initialize a regular dictionary to store sales data by region (wilaya_name)
    sales_by_region = {}

    # Query orders for the specific product and aggregate by region (wilaya_name)
    orders = Order.objects.filter(product=product, is_ordered=True)

    # Aggregate sales by wilaya_name (region)
    for order in orders:
        region_key = order.state # Access the wilaya_name from the JSON
        sales_value = order.order_total

        # If the region already exists in the dictionary, add to it, otherwise initialize it
        if region_key in sales_by_region:
            sales_by_region[region_key] += sales_value
        else:
            sales_by_region[region_key] = sales_value

    # Return the sales data by region
    return sales_by_region





from django.db.models import Sum, F, DecimalField

def get_top_selling_variations_for_product(product):
    """
    Get the top 5 selling variations for a specific product based on total sales.
    Returns a list of variations sorted by total sales and categorized by variant type.
    """
    # Initialize an empty list to store the data for top 5 variations
    top_variations_data = []

    # Query the OrderProduct model for orders related to the specific product and join with variations
    order_products = OrderProduct.objects.filter(product=product, ordered=True).values(
        'variations__id', 
        'variations__color__name', 
        'variations__size', 
        'variations__variant_type', 
        'variations__price'
    ).annotate(
        total_sales=Sum(F('quantity') * F('product_price'), output_field=DecimalField()),  # Explicitly set output_field
        total_quantity_sold=Sum('quantity')  # Total quantity sold
    ).order_by('-total_sales')  # Sort by total sales in descending order

    # Get the top 5 variations based on total sales
    for order_product in order_products[:5]:
        variation_info = {
            'variation_id': order_product['variations__id'],
            'total_sales': order_product['total_sales'],
            'quantity_sold': order_product['total_quantity_sold'],
            'price': order_product['variations__price'],
            'variant_type': order_product['variations__variant_type'],
        }

        # Add additional details based on variant type
        if order_product['variations__variant_type'] == 'color':
            variation_info['color'] = order_product['variations__color__name']
        elif order_product['variations__variant_type'] == 'size':
            variation_info['size'] = order_product['variations__size']
        elif order_product['variations__variant_type'] == 'size_and_color':
            variation_info['color'] = order_product['variations__color__name']
            variation_info['size'] = order_product['variations__size']

        top_variations_data.append(variation_info)

    return top_variations_data




from django.db.models import Avg, Count, Q

def get_product_feedback(product):
    """
    Get customer feedback for a specific product.
    Returns average rating, total reviews, and a breakdown of positive, neutral, and negative reviews.
    """
    # Filter reviews for the product and with status=True (approved reviews)
    reviews = ReviewRating.objects.filter(product=product, status=True)

    # Calculate the average rating
    average_rating = reviews.aggregate(average=Avg('rating'))['average'] or 0

    # Calculate the total number of reviews
    total_reviews = reviews.count()

    # Breakdown of reviews by sentiment
    positive_reviews = reviews.filter(rating__gte=4).count()
    neutral_reviews = reviews.filter(rating__gte=2, rating__lt=4).count()
    negative_reviews = reviews.filter(rating__lt=2).count()

    # Calculate percentages
    if total_reviews > 0:
        positive_percentage = (positive_reviews / total_reviews) * 100
        neutral_percentage = (neutral_reviews / total_reviews) * 100
        negative_percentage = (negative_reviews / total_reviews) * 100
    else:
        positive_percentage = neutral_percentage = negative_percentage = 0

    # Return feedback data
    return {
        'average_rating': round(average_rating, 1),
        'total_reviews': total_reviews,
        'positive_percentage': round(positive_percentage, 1),
        'neutral_percentage': round(neutral_percentage, 1),
        'negative_percentage': round(negative_percentage, 1),
    }





def get_inventory_status(product):
    """
    Get inventory status, stockouts, and reorder points for a product.
    Returns stock level, stockout alerts, and reorder status.
    """
    # Get variations of the product
    variations = Variation.objects.filter(product=product)
    
    stockout_alerts = []
    total_quantity_in_stock = 0
    reorder_threshold = 20  # Set your reorder threshold here
    current_stock_data = []
    
    # Iterate through each variation
    for variation in variations:
        quantity_sold = OrderProduct.objects.filter(variations=variation).aggregate(
            total_sold=Sum('quantity')
        )['total_sold'] or 0
        
        # Check current stock level for each variation
        current_stock = variation.quantity - quantity_sold
        total_quantity_in_stock += current_stock
        
        # Check if stock is below reorder point
        is_below_reorder_point = current_stock <= reorder_threshold
        
        # Track stockouts: If the stock is zero, add an alert
        if current_stock == 0:
            stockout_alerts.append({
                'variation': variation,
                'last_stockout_date': datetime.now().strftime("%Y-%m-%d"),
                'is_stockout': True,
            })
        
        # Store current stock status for the chart
        current_stock_data.append({
            'variation': variation,
            'current_stock': current_stock,
            'is_below_reorder': is_below_reorder_point,
        })
    
    return {
        'total_quantity_in_stock': total_quantity_in_stock,
        'reorder_threshold': reorder_threshold,
        'stockout_alerts': stockout_alerts,
        'current_stock_data': current_stock_data,
    }


def customer_sales_analysis_for_product(product):
    """
    Calculate and return the profit per customer for a specific product.
    """
    # Filter orders for the specific product
    aggregated_data = (
        OrderProduct.objects.filter(product=product, ordered=True)  # Filter by product and ordered status
        .values('user')  # Group by purchasing user
        .annotate(
            total_spent=Sum(F('product_price') * F('quantity'), output_field=DecimalField())  # Total spent on the product
        )
    )

    customer_data = []

    for data in aggregated_data:
        try:
            # Get purchasing user's account and profile
            customer = Account.objects.get(id=data['user'])
            user_profile = UserProfile.objects.get(user=customer)
        except ObjectDoesNotExist:
            customer = None
            user_profile = None

        # Assuming cost_price is available on the Product model or OrderProduct model
        cost_price = product.cost_price if hasattr(product, 'cost_price') else 0
        profit_per_customer = data['total_spent'] - (cost_price * OrderProduct.objects.filter(product=product, user=customer).count())

        customer_data.append({
            'user': customer,
            'total_spent': data['total_spent'] or 0.0,
            'profit': profit_per_customer,
            'profile_picture': user_profile.profile_picture.url if user_profile and user_profile.profile_picture else None,
            'email': customer.email if customer else None,
            'username': customer.username if customer else None,
        })

    return customer_data


import numpy as np
def generate_price_sensitivity_data(product):
    """
    Generate price sensitivity data for a product's most relevant variation.
    """
    # Get the primary variation (e.g., the most sold or a default one)
    primary_variation = (
        Variation.objects.filter(product=product, is_active=True)
        .annotate(total_sold=Sum('orderproduct__quantity'))
        .order_by('-total_sold')
        .first()
    )

    if not primary_variation:
        return None, None, None, "No active variations found for this product."

    base_price = float(primary_variation.price)
    base_sales = (
        OrderProduct.objects.filter(variations=primary_variation, ordered=True)
        .aggregate(total_sales=Sum('quantity'))['total_sales']
        or 0
    )
    base_cost_price = float(product.cost_price)

    # Price adjustment percentages (from -20% to +20%)
    price_adjustments = np.arange(-0.2, 0.21, 0.05)  # Adjustments in 5% increments

    price_data = []
    sales_data = []
    profit_data = []

    for adjustment in price_adjustments:
        adjusted_price = base_price * (1 + adjustment)
        sales_volume = base_sales * (1 - adjustment * 2)  # Example sales elasticity
        profitability = (adjusted_price - base_cost_price) * sales_volume

        price_data.append(round(adjusted_price, 2))
        sales_data.append(max(round(sales_volume, 2), 0))  # Ensure sales volume is not negative
        profit_data.append(round(profitability, 2))

    return price_data, sales_data, profit_data, None







def Product_Profit_Detail(request, product_slug):
    """
    Analyze detailed profits for a specific product.
    """
    user = request.user

    # Get all products for the logged-in user
    products = Product.objects.filter(buyer=user)

    # Get the product by slug (ensure it belongs to the user)
    product = get_object_or_404(Product, slug=product_slug, buyer=user)

    # Get transaction data for this product
    cost_price = product.cost_price or Decimal('0.00')

    # Total Deposits (cost_price * quantity)
    total_deposits_with_quantity = OrderProduct.objects.filter(
        product=product, ordered=True
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('product__cost_price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or Decimal('0.00')

    # Total Withdrawals (Sum((product_price - cost_price) * quantity))
    total_withdrawals = OrderProduct.objects.filter(
        product=product, ordered=True
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('product_price') * F('quantity'),
                output_field=DecimalField()
            )
        )
    )['total'] or Decimal('0.00')

    # Total Quantity Sold
    total_quantity = OrderProduct.objects.filter(
        product=product, ordered=True
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Balance (Total Profit)
    balance = total_withdrawals - total_deposits_with_quantity

    # Get weekly sales data for the product
    weekly_sales_data = get_weekly_sales_data_for_product(product)

    # Get monthly sales data for the product
    monthly_sales_data = get_monthly_sales_data_for_product(product)

    # Get weekly sales data for the product (broken down into 4 weeks per month)
    monthly_sales_data2 = get_weekly_sales_data_for_product_per_month(product)

    # Get sales data by region for the product
    sales_by_region = get_sales_by_region_for_product(product)

    # Get the top 5 selling variations for this product
    top_selling_variations = get_top_selling_variations_for_product(product)

    # Get feedback data for the product
    feedback_data = get_product_feedback(product)

    # Get inventory data for the product
    inventory_data = get_inventory_status(product)

    # Get customer sales analysis for the product
    product_profit_data = customer_sales_analysis_for_product(product)

     # Generate price sensitivity data
     # Generate price sensitivity data for the product
    price_data, sales_data, profit_data, error = generate_price_sensitivity_data(product)

    if error:
        return render(request, 'analytics/product_profit_detail.html', {
            'error': error,
            'product': product,
        })

   

    # Return the analysis data to the template
    context = {
        'product': product,
        'cost_price': cost_price,
        'total_deposits_with_quantity': total_deposits_with_quantity,
        'total_withdrawals': total_withdrawals,
        'balance': balance,
        'total_quantity': total_quantity,
        'weekly_sales_data': weekly_sales_data,
        'monthly_sales_data': monthly_sales_data,
        'monthly_sales_data2': monthly_sales_data2,
        'sales_by_region': sales_by_region,
        'top_selling_variations': top_selling_variations,
        'feedback_data': feedback_data,
        'inventory_data': inventory_data,
        'product_profit_data': product_profit_data,
        'products': products,  # Add products to the context
        'price_data': price_data,
        'sales_data': sales_data,
        'profit_data': profit_data,

        
    }

    return render(request, 'analytics/product_profit_detail.html', context)




def show_all_costumers_by_product(request, product_slug, product_id):

    # Get the product by slug (ensure it belongs to the user)
    product = get_object_or_404(Product, slug=product_slug, id = product_id)

    costumer = customer_sales_analysis_for_product(product)

    context = {
     
      'costumer': costumer,
    }
    return render(request, 'analytics/costumers_by_product.html', context) 




""" End Product Profit Analytics """

def Costumer_Sales(request):
	user = request.user
    
	customer_data = customer_sales_analysis(user)

	context = {
     'customer_data': customer_data,
	}

	return render(request, 'analytics/costumer_sales.html', context)

def State_Sales(request):
    user = request.user

    # Get the total sales globally (all-time sales for the user)
    total_sales_all_time = OrderProduct.objects.filter(
        product__buyer=user
    ).aggregate(total_sales=Sum('product_price'))['total_sales'] or 0

    # Aggregate total sales by state globally
    sales_by_state_all_time = Order.objects.filter(
        product__buyer=user
    ).values('state').annotate(
        total_sales=Sum('orderproduct__product_price')
    ).order_by('-total_sales')

    # Calculate the percentage of total sales for each state
    state_sales_data = []
    for state_item in sales_by_state_all_time:
        state = state_item['state']
        current_sales = state_item['total_sales']

        # Calculate the percentage of total sales for the state
        percentage_of_total = (current_sales / total_sales_all_time) * 100 if total_sales_all_time > 0 else 0
        percentage_of_total = round(percentage_of_total, 2)

        state_sales_data.append({
            'state': state,
            'current_sales': current_sales,
            'percentage_of_total': percentage_of_total,
        })

    context = {
        'state_data': state_sales_data,
        'total_sales_all_time': total_sales_all_time,
    }

    return render(request, 'analytics/state_sales.html', context)

