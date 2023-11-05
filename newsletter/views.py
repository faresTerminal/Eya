from django.core.mail import send_mail
from django.shortcuts import render, redirect
from .forms import EmailSubscriptionForm
from store.models import Daily_slide
from .models import EmailSubscription

def subscribe_to_newsletter(request):
    if request.method == 'POST':
        form = EmailSubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']  # Get the email from the form
            # Check if an email subscription with the same email exists
            if EmailSubscription.objects.filter(email=email).exists():
                # Email address is already subscribed
                return redirect('newsletter:already_subscribed') 
            else:
                form.save()
                # Send an email to the provided email address
                send_mail(
                    'Thank You for Subscribing',
                    'You are now subscribed to our newsletter.',
                    'Molla Store',  # Replace with your email address
                    [email],
                    fail_silently=False  # Set to True to suppress errors (use False for debugging)
                )
                return redirect('newsletter:thank_you')  # Redirect to a thank you page
    else:
        form = EmailSubscriptionForm()
    return render(request, 'home.html', {'form': form})


def send_newsletter(request):
    # Fetch the latest deals
    
    return render(request, 'newsletter/thank_you.html')

def already_subscribed(request):
	return render(request, 'newsletter/already_subscribed.html')



# send update to all user subscribed


def send_daily_slide_email(request):
    # Retrieve the Daily_Slide you want to send
    daily_slide = Daily_slide.objects.get()

    # Get the list of email addresses from the database
    email_subscriptions = EmailSubscription.objects.values_list('email', flat=True)

    # Compose and send the email to all subscribers
    subject = 'Daily Slide Update'
    message = f'Check out today\'s Daily Slide: {daily_slide.sub_title}\n{daily_slide.big_title}\n{daily_slide.description}'
    from_email = 'your_email@example.com'  # Replace with your email address

    send_mail(subject, message, from_email, email_subscriptions, fail_silently=False)

    # Redirect or render a confirmation page
    return render(request, 'newsletter/confirmation.html')



