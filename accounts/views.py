from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm, UserSocialForm
from .models import Account, UserProfile, SellerReview, Shop_Social_User
from accounts.forms import UserProfileForm, SellerReviewForm
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from orders.models import Order, OrderProduct
# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from store.models import Product, Variation
from carts.views import _cart_id
from carts.models import Cart, CartItem
import requests
from django.http import Http404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseBadRequest
from django.db.models import Avg, Count, Prefetch
from django.utils.timezone import now, timedelta
from django.utils import timezone

from django.conf import settings

from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from .forms import RegistrationForm
from .models import Account  # Replace with your user model if different
from affiliate.models import Affiliate, AffiliateReferral

from django.core.mail import send_mail

import random
import string
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string


from django.http import JsonResponse


def generate_confirmation_code():
    # Generate a random 6-digit confirmation code
    return ''.join(random.choices(string.digits, k=6))

def send_confirmation_email(user):
    confirmation_code = generate_confirmation_code()
    user.confirmation_code = confirmation_code  # Store the code in the user model
    user.confirmation_code_sent_at = timezone.now()
    user.save()

    # Prepare email content
    subject = 'Activate Your Account'
    html_message = render_to_string('accounts/account_verification_email.html', {
        'user': user,
        'confirmation_code': confirmation_code,
        'site_url': 'http://yourwebsite.com',  # Replace with your site URL
        'support_url': 'http://yourwebsite.com/support',  # Replace with your support URL
    })

    # Send the email
    send_mail(subject, "", 'no-reply@yourwebsite.com', [user.email], html_message=html_message)

def register(request):
    if request.user.is_authenticated:
        return redirect('home')  # Or redirect to another page like user dashboard

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Extract cleaned data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            affiliate_code = form.cleaned_data['affiliate_code']
            username = email.split("@")[0]

            # Create and save the user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            

            # Assign a 3-month trial period
            user.is_trial = True
            user.trial_end_date = timezone.now() + timedelta(days=30)  # 3 months trial period

            # Handle affiliate referral (if applicable)
            if affiliate_code:
                try:
                    affiliate = Affiliate.objects.get(affiliate_code=affiliate_code)
                    user.referred_by = affiliate.user
                    user.save()

                    # Create AffiliateReferral record
                    AffiliateReferral.objects.create(
                        affiliate=affiliate,
                        referred_user=user
                    )
                    messages.success(request, f'You were referred by {affiliate.user.email}.')
                except Affiliate.DoesNotExist:
                    messages.warning(request, 'Invalid affiliate code. Registration continued without referral.')

            # Send confirmation email with code
            send_confirmation_email(user)

            return redirect('verify_confirmation', user_id=user.id)  # Redirect to a confirmation page
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def expired_code_page(request, user_id):
    return render(request, 'accounts/error_page.html', {'user_id': user_id})




def resend_confirmation_code(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    # Send a new confirmation code (similar to how you did before)
    send_confirmation_email(user)
    return redirect('verify_confirmation', user_id=user.id)





def verify_confirmation(request, user_id):
    user = Account.objects.get(id=user_id)
    expiration_time = user.confirmation_code_sent_at + timedelta(seconds=90)
    remaining_time = expiration_time - timezone.now()

    # If confirmation code has expired
    if remaining_time.total_seconds() <= 0:
        messages.error(request, 'Your confirmation code has expired.')
        return redirect('error_page',  user_id=user.id)  # Redirect to the error page
    
    if request.method == 'POST':
        confirmation_code = request.POST['confirmation_code']
        if confirmation_code == user.confirmation_code:
            user.is_active = True
            user.is_confirmed = True
            user.save()
            messages.success(request, 'Your account has been successfully activated.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid confirmation code.')

    return render(request, 'accounts/confirm_account.html', {
        'user': user,
        'remaining_time': remaining_time.total_seconds(),
        'user_id': user.id  # Pass user_id to the template
    })





   





def login(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to the home page or user dashboard

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Authenticate user
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            # Debugging: Print user details and trial/subscription status
            print(f"User authenticated: {user.email}, is_trial: {user.is_trial}, subscription_active: {user.subscription_active}")

            current_time = now()

            # Check trial expiration (only if trial_end_date is not None)
            if user.is_trial and user.trial_end_date and user.trial_end_date < current_time:
                user.is_trial = False
                user.subscription_active = False
                user.save()
                messages.error(request, 'Your trial has expired. Please subscribe to continue.')
                auth.login(request, user)
                return redirect('payment:trial_expired')

            # Check subscription expiration (only if subscription_expiry_date is not None)
            if not user.is_trial and (
                not user.subscription_active or 
                (user.subscription_expiry_date and user.subscription_expiry_date < current_time)
            ):
                user.subscription_active = False
                user.save()
                messages.error(request, 'Your subscription has expired. Please renew to continue.')
                auth.login(request, user)
                return redirect('payment:trial_expired')

            # Handle cart merging
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_items = CartItem.objects.filter(cart=cart)
                for item in cart_items:
                    item.user = user
                    item.save()
            except Cart.DoesNotExist:
                pass

            # Debugging: Confirm login success
            auth.login(request, user)
            print(f"User logged in: {user.email}")
            messages.success(request, 'You are now logged in.')

            # Redirect to the next page or home if no next URL
            next_url = request.GET.get('next', 'home')
            print(f"Redirecting to: {next_url}")
            return redirect(next_url)

        else:
            # Invalid credentials
            messages.error(request, 'Invalid login credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')




@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')
















@login_required(login_url = 'login')
def dashboard(request):
    current_user = request.user
    orders = Order.objects.order_by('created_at').filter(user_id = current_user.id, is_ordered = True)
    orders_count = orders.count()

    
    
    try:
        userprofile = UserProfile.objects.get(user_id=current_user.id)
    except UserProfile.DoesNotExist:
        userprofile = None  # Set userprofile to None if it doesn't exist
        
    context = {
    'orders_count': orders_count,
    'userprofile': userprofile,
    
    
    }
    return render(request, 'accounts/dashboard.html', context)




    

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')




def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('login')



def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')


@login_required(login_url='login')
def edit_profile(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile(user=request.user)
        userprofile.save()

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
        
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def my_orders(request):
    # Get the status filter from the query parameters
    status_filter = request.GET.get('status')

    # Retrieve orders for the logged-in user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Apply status filter if it exists
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Paginate the filtered orders
    paginator = Paginator(orders, 10)  # 10 orders per page
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    context = {
        'orders': paged_orders,
        'status_choices': Order.STATUS,  # Pass the status choices for the dropdown
        'selected_status': status_filter,  # Pass the currently selected status to preselect in the dropdown
    }
    return render(request, 'accounts/my_orders.html', context)






@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):

    order = Order.objects.get(order_number=order_id)

    order_detail = OrderProduct.objects.filter(order=order)
    #order = Order.objects.get(order_number=order_id)
    
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    
   

    

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    
    }
    return render(request, 'accounts/order_detail.html', context)


def register_confirme_link(request):
    return render (request, 'accounts/register_confirme_link.html')



def printing(request):
      current_user = request.user
      complete_orders = Order.objects.filter(product__buyer=current_user, status = 'Completed').order_by('-id')

      paginator = Paginator(complete_orders, 10)
      page = request.GET.get('page')
      paged_products = paginator.get_page(page)
      product_count = complete_orders.count()

      context = {
      'complete_orders': paged_products,
      } 
      return render(request, 'accounts/printing.html', context)




def remove_completed_orders(request, order_id):
    # Retrieve the order or return a 404 response if it doesn't exist
    order = get_object_or_404(Order, id=order_id, product__buyer=request.user, status='Completed')

    if request.user.is_authenticated:
       messages.error(request, 'Order Removed !')
       order.delete()

    return redirect('printing') 

def User_Products(request):
    current_user = request.user
    products = Product.objects.filter(buyer = current_user, is_available = True)

    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
     'products': paged_products,
    }
    return render(request, 'accounts/edit_products.html', context)


   


def remove_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Assuming you want to confirm the deletion with a POST request
        product.delete()
        messages.error(request, 'Product Removed successfully.')
        return redirect('User_Products')  # Redirect to a page showing the list of remaining products

    return render(request, 'accounts/remove_product.html', {'product': product})

    


   






def Seller_Info(request, username):
    # Get variant information for each featured product
    variants_prefetch = Prefetch(
        'variations',
        queryset=Variation.objects.filter(is_active=True),
        to_attr='variants'
    )
    
    # Fetch the products associated with the seller (buyer)
    products = Product.objects.filter(buyer__username=username, is_available=True).prefetch_related(variants_prefetch)

    if not products:
        return render(request, 'accounts/userPoster.html', {
            'error_message': 'No seller found with this username.'
        })

    # Get the seller (buyer) from the product
    user = products.first().buyer

    # Fetch the related UserProfile, if it exists
    user_profile = UserProfile.objects.filter(user=user).first()
     # Fetch the social media links for the seller, if available
    shop_social = user_profile.shop_social if user_profile else None

    # Get the reviews
    reviews = SellerReview.objects.filter(reviewer=user)
  
    review_count = reviews.count()
    

    # Set up pagination for the products
    paginator = Paginator(products, 3)  # Show 3 products per page
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    
    # Count the number of products
    product_count = products.count()

    # Pass all the information to the context
    context = {
        'user': user,
        'user_profile': user_profile,
        'products': paged_products,
        'shop_social': shop_social,
        'product_count': product_count,
        'reviews': reviews,
        'review_count': review_count,
    }

    # Render the seller profile and products page
    return render(request, 'accounts/userPoster.html', context)


# Top products for seller
def top_seller_products_view(request, username):
    # Get variant information for each featured product
    variants_prefetch = Prefetch(
        'variations',
        queryset=Variation.objects.filter(is_active=True),
        to_attr='variants'
    )
    
    # Fetch the products associated with the seller (buyer)
    products = Product.objects.filter(buyer__username=username).prefetch_related(variants_prefetch)

    if not products:
        return render(request, 'accounts/top_products.html', {
            'error_message': 'No seller found with this username.'
        })

    # Get the seller (buyer) from the product
    user = products.first().buyer

    # Fetch top 5 rated products for this seller
    top_seller_products = products.annotate(
        average_rating=Avg('reviewrating__rating')
    ).order_by('-average_rating')[:5]

    # Set up pagination for the products
    paginator = Paginator(top_seller_products, 4)  # Show 4 products per page
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    # Pass top products to the context
    context = {
        'user': user,
        'top_seller_products': paged_products,  # Pass top products to context
    }

    # Render the top products page
    return render(request, 'accounts/top_products.html', context)



def seller_reviews_view(request, username):
    # Fetch the products associated with the seller (buyer)
    products = Product.objects.filter(buyer__username=username)

    if not products:
        return render(request, 'accounts/seller_reviews.html', {
            'error_message': 'No seller found with this username.'
        })

    # Get the seller (buyer) from the product
    user = products.first().buyer

    # Fetch reviews related to the seller
    reviews = SellerReview.objects.filter(seller=user).order_by('-id')[:4]

    # Handle review form submission
    if request.method == 'POST':
        form = SellerReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.seller = user
            review.reviewer = request.user
            review.save()
            messages.success(request, 'Your Review Saved!.')
            return redirect('seller_reviews', username=user.username)
    else:
        form = SellerReviewForm()

    context = {
        'user': user,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'accounts/seller_reviews.html', context)



def seller_contact(request, username):
    # Fetch the products associated with the seller (buyer)
    products = Product.objects.filter(buyer__username=username).first()

    if not products:
        return render(request, 'accounts/seller_contact.html', {
            'error_message': 'No seller found with this username.'
        })

    # Get the seller (buyer) from the product
    user = products.buyer

    # Fetch the related UserProfile, if it exists
    user_profile = UserProfile.objects.filter(user=user).first()

    # Fetch the social media links for the seller, if available
    shop_social = user_profile.shop_social if user_profile else None

    context = {
        'user': user,
        'shop_social': shop_social,
    }

    return render(request, 'accounts/seller_contact.html', context)


def social_media(request):

    current_user = request.user

    shop_social_user = Shop_Social_User.objects.order_by('id').filter(user_social= current_user).first()
    
    context = {
    'shop_social_user': shop_social_user,

    }


    return render(request, 'accounts/social_media.html', context)


def add_social_media(request):
    if request.method == 'POST':
        social_media_form = UserSocialForm(request.POST)
        if social_media_form.is_valid():
            # Save the social media form instance without committing to the database
            social_media = social_media_form.save(commit=False)
            social_media.user_social = request.user
            social_media.save()  # Save the new Shop_Social_User instance

            # Check if the current user has an existing UserProfile and update it
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.shop_social = social_media
                user_profile.save()  # Save the UserProfile with the updated shop_social field
            except UserProfile.DoesNotExist:
                # If no UserProfile exists, create one and set the shop_social field
                UserProfile.objects.create(user=request.user, shop_social=social_media)
            messages.success(request, 'Social Media Accounts Added')
            return redirect('social_media')
    else:
        social_media_form = UserSocialForm()

    return render(request, 'accounts/add_social_media.html', {'social_media_form': social_media_form})


@login_required
def edit_social_media(request):
    # Get the current user's social media profile or return a 404 if not found
    social_media = get_object_or_404(Shop_Social_User, user_social=request.user)

    if request.method == 'POST':
        # Pass the existing instance to the form for editing
        social_media_form = UserSocialForm(request.POST, instance=social_media)
        if social_media_form.is_valid():
            social_media = social_media_form.save(commit=False)
            social_media.user_social = request.user
            social_media.save()
            messages.success(request, 'Social Media Accounts Updated')
            return redirect('social_media')  # Redirect to the social media overview page
    else:
        # Prepopulate the form with the current data
        social_media_form = UserSocialForm(instance=social_media)

    return render(request, 'accounts/edit_social_media.html', {'social_media_form': social_media_form})





#For Payment

def check_expired_accounts():
    # Expire trials
    expired_trials = Account.objects.filter(is_trial=True, trial_end_date__lt=now())
    expired_trials.update(is_trial=False, subscription_active=False)

    # Expire subscriptions
    expired_subscriptions = Account.objects.filter(
        subscription_active=True, subscription_expiry_date__lt=now()
    )
    expired_subscriptions.update(subscription_active=False)





from twilio.rest import Client
from django.conf import settings
import random

def send_sms(phone_number):
    # Generate a verification code
    verification_code = ''.join(random.choices('0123456789', k=6))

    # Store this verification code in the user's model (in a new field) for later validation

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Send the SMS
        message = client.messages.create(
            body=f"Your verification code is {verification_code}",
            from_=settings.TWILIO_PHONE_NUMBER,  # Twilio phone number
            to=phone_number
        )
        return verification_code  # You can save this code in the user model for later validation

    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
