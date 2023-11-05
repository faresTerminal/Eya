
from django.shortcuts import render, get_object_or_404, redirect
from .models import Comparison
from store.models import Product 
from category.models import Category 
from django.http import JsonResponse
# Create your views here.







def product_search(request):
    letter = request.GET.get('letter', '')  # Get the specific letter from the URL parameter 'letter'

    # Fetch product names containing the specified letter
    suggestions = Product.objects.filter(product_name__icontains=letter).values_list('product_name', flat=True)

    context = {
        'letter': letter,
        'suggestions': suggestions,
    }

    return render(request, 'comparision/select_products.html', context)




def comparison_result(request):
    # Retrieve the most recent comparison
    latest_comparison = Comparison.objects.latest('id')
    context = {
    'comparison': latest_comparison,
    }
    return render(request, 'comparision/compare_result.html', context)
