from django.shortcuts import render, get_object_or_404
from store.models import Product
from category.models import Category


# Create your views here.
def show_category(request):
	
	
	
	

	return render(request, 'category/category_list.html')