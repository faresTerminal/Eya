from django.shortcuts import render

def custom_404(request, exception):
    context = {
        "error_message": "We are sorry, the page you've requested is not available."
    }
    return render(request, 'includes/404.html', context, status=404)

