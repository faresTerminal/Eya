from .models import UserProfile

def user_profile_picture(request):
    profile_picture = None
    if request.user.is_authenticated:
        try:
            profile_picture = UserProfile.objects.get(user=request.user).profile_picture
        except UserProfile.DoesNotExist:
            pass

    return {'user_profile_picture': profile_picture}
