from .models import UserProfile, Shop_Social

def user_profile_picture(request):
    profile_picture = None
    if request.user.is_authenticated:
        try:
            profile_picture = UserProfile.objects.get(user=request.user).profile_picture
        except UserProfile.DoesNotExist:
            pass

    return {'user_profile_picture': profile_picture}




def social_links(request):
    # Get the first social links object, or handle the case where no object exists
    social_links = Shop_Social.objects.first()
    return {'social_links': social_links}