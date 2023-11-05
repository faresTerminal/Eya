from .models import Category, SubCategory

def menu_links(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    category_dict = {}  # Create an empty dictionary to store the data

    for category in categories:
        # Filter subcategories related to the current category
        related_subcategories = subcategories.filter(category=category)
        category_dict[category] = related_subcategories

    return {'categories': categories, 'category_dict': category_dict}

