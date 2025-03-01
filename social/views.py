from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import FacebookPixel
from .forms import FacebookPixelForm



def manage_pixels(request):
    if request.method == 'POST':
        form = FacebookPixelForm(request.POST)
        if form.is_valid():
            pixel = form.save(commit=False)
            pixel.user = request.user
            pixel.save()
            return redirect('manage_pixels')  # Redirect to the same page after saving
    else:
        form = FacebookPixelForm()

    user_pixels = FacebookPixel.objects.filter(user=request.user if request.user.is_authenticated else None)
    return render(request, 'social/manage_pixels.html', {
        'form': form,
        'user_pixels': user_pixels,
    })




@login_required
def delete_pixel(request, pixel_id):
    pixel = FacebookPixel.objects.get(id=pixel_id, user=request.user)
    if pixel:
        pixel.delete()
    return redirect('manage_pixels')

