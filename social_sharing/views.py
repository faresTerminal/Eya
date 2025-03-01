# views.py
import requests
from django.conf import settings
from django.shortcuts import redirect

def facebook_login(request):
    facebook_login_url = (
        "https://www.facebook.com/v15.0/dialog/oauth?"
        f"client_id={settings.FACEBOOK_APP_ID}"
        f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
        "&scope=public_profile,email,pages_manage_posts,pages_show_list"
    )
    return redirect(facebook_login_url)


# views.py
def facebook_callback(request):
    code = request.GET.get('code')
    if code:
        # Exchange the code for an access token
        token_url = (
            "https://graph.facebook.com/v15.0/oauth/access_token?"
            f"client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
            f"&client_secret={settings.FACEBOOK_APP_SECRET}"
            f"&code={code}"
        )
        response = requests.get(token_url)
        access_token = response.json().get('access_token')

        if access_token:
            # Now you can use the access token to post on Facebook
            share_url = 'https://graph.facebook.com/v15.0/me/feed'
            post_data = {
                'message': 'Check out this amazing product!',
                'link': 'http://127.0.0.1:8000/en/store/products/books-media/tasla-product-new-phone/',
                'access_token': access_token
            }
            post_response = requests.post(share_url, data=post_data)
            if post_response.status_code == 200:
                return redirect('success_url')
            else:
                return redirect('error_url')
    return redirect('login')
