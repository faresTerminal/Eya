from category.models import Category
# we create file context processors to dispaly category menu in all pages
def menu_links_products(request):
    products_links = Category.objects.all()
    return dict(products_links=products_links)
