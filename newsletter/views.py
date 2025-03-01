
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Subscriber
from .forms import SubscriptionForm
from store.models import Daily_slide
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def subscribe(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if the email already exists
            if Subscriber.objects.filter(email=email, is_active=True).exists():
                messages.info(request, "This email is already subscribed!")
            else:
                form.save()
                return redirect('newsletter:thank_you')
            return redirect('home')
    else:
        form = SubscriptionForm()
    return render(request, 'newsletter/already_subscribed.html', {'form': form})


def send_newsletter(newsletter_id):
    newsletter = Newsletter.objects.get(id=newsletter_id)
    subscribers = Subscriber.objects.filter(is_active=True)

    for subscriber in subscribers:
        send_mail(
            subject=newsletter.subject,
            message=newsletter.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            fail_silently=False,
        )

    newsletter.sent = True
    newsletter.save()


# send update to all user subscribed





def send_daily_slide_email(request):
    # Retrieve the Daily Slide to send
    daily_slide = Daily_slide.objects.latest('created_at')  # Get the latest slide

    # Get the list of email addresses from the Subscriber model
    email_subscriptions = Subscriber.objects.filter(is_active=True).values_list('email', flat=True)

    # Email subject and from email
    subject = 'Eco-dz Shopping'
    from_email = settings.DEFAULT_FROM_EMAIL

    # Render HTML content for the email
    html_content = render_to_string('newsletter/daily_slide_email.html', {'daily_slide': daily_slide})
    text_content = strip_tags(html_content)  # Plain-text fallback

    # Send email to each subscriber
    for email in email_subscriptions:
        msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

    # Redirect or render a confirmation page
    return render(request, 'newsletter/confirmation.html')



def send_newsletter(request):
    # Fetch the latest deals
    
    return render(request, 'newsletter/thank_you.html')


def unsubscribe(request):
    # Retrieve the email from the query parameter
    email = request.GET.get('email')
    if email:
        try:
            # Find the subscriber and set is_active to False
            subscriber = Subscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            messages.success(request, "You have been unsubscribed from the newsletter.")
        except Subscriber.DoesNotExist:
            messages.error(request, "Email address not found.")
    else:
        messages.error(request, "Invalid unsubscribe request.")
    
    # Redirect to a confirmation page
    return render(request, 'newsletter/unsubscribe_confirmation.html')