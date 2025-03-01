from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Conversation, Message
from store.models import Product
from accounts.models import Account
from notification.models import Notification  # Import your Notification model
from .forms import MessageForm
from django.db.models import Q




@login_required
def start_conversation(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    buyer = request.user
    seller = product.buyer

    conversation, created = Conversation.objects.get_or_create(
        seller=seller,
        buyer=buyer,
        product=product
    )

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = buyer  # The sender is the buyer
            message.save()

            # Retrieve the profile picture URL of the buyer
            buyer_profile_picture_url = buyer.userprofile.profile_picture.url if buyer.userprofile.profile_picture else '/static/default_profile_picture.png'

            # Create a notification for the seller
            if seller != buyer:  # Ensure the notification is sent to the other user
                Notification.objects.create(
                    sender=buyer,
                    recipient=seller,
                    conversation=conversation,
                    message=f"New message from {buyer.username} in conversation about\n {product.product_name}",
                    url=f'/chat/conversation/{conversation.id}/',
                    profile_picture_url=buyer_profile_picture_url  # Pass the profile picture URL here
                )

            # Handle AJAX requests
            if request.is_ajax():
                messages = conversation.messages.all().order_by('timestamp')
                return render(request, 'chat/conversation_popup.html', {
                    'conversation': conversation,
                    'messages': messages,
                    'form': form,
                    'seller_profile_picture': seller.userprofile.profile_picture.url if seller.userprofile.profile_picture else None
                })

            return redirect('view_conversation', conversation_id=conversation.id)

    else:
        form = MessageForm()

    # Load messages if not a POST request
    messages = conversation.messages.all().order_by('timestamp')
    
    return render(request, 'chat/conversation_popup.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'seller_profile_picture': seller.userprofile.profile_picture.url if seller.userprofile.profile_picture else None
    })









@login_required
def view_conversation(request, conversation_id):
    # Get the specific conversation
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # Mark all messages as read when the conversation is viewed by the current user
    conversation.messages.filter(~Q(sender=request.user)).update(is_read=True)

    # Retrieve all conversations for the user to display
    user = request.user
    conversations = Conversation.objects.filter(
        seller=user
    ).select_related('buyer').union(
        Conversation.objects.filter(buyer=user).select_related('seller')
    ).order_by('-created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()

            # Retrieve the profile picture URL of the buyer
            buyer_profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else '/static/default_profile_picture.png'

            # Notify the appropriate user
            if request.user == conversation.seller:
                Notification.objects.create(
                    sender=request.user,
                    recipient=conversation.buyer,
                    conversation=conversation,
                    message=f"New message from {conversation.seller.username}",
                    url=f'/chat/conversation/{conversation.id}/',
                    profile_picture_url=buyer_profile_picture_url
                )
            else:
                Notification.objects.create(
                    sender=request.user,
                    recipient=conversation.seller,
                    conversation=conversation,
                    message=f"New message from {conversation.buyer.username}",
                    url=f'/chat/conversation/{conversation.id}/',
                    profile_picture_url=buyer_profile_picture_url
                )

            # Handle AJAX requests
            if request.is_ajax():
                return render(request, 'chat/single_message.html', {'message': message})

            return redirect('view_conversation', conversation_id=conversation.id)
    else:
        form = MessageForm()

    # Get all messages for the specific conversation
    messages = conversation.messages.all().order_by('timestamp')

    return render(request, 'chat/view_conversation_popup.html', {
        'conversation': conversation,
        'messages': messages,
        'form': form,
        'conversations': conversations  # Pass all conversations to the template
    })






@login_required
def conversation_list_view(request):
    user = request.user

    # Get the latest six conversations where the user is either the buyer or seller
    conversations = (
        Conversation.objects.filter(seller=user)
        .select_related('buyer', 'product')
        .union(
            Conversation.objects.filter(buyer=user).select_related('seller', 'product')
        )
        .order_by('-created_at')  # Order by creation date in descending order
    )[:6]  # Limit to the last 6 conversations

    # Initialize a list to hold the latest conversations with their latest messages
    conversation_list = []
    
    # Count unread notifications
    unread_notifications_count = request.user.received_notifications.filter(read=False).count()

    for conversation in conversations:
        # Get all messages for the conversation
        messages = conversation.messages.all().order_by('timestamp')
        
        # Get the latest message if it exists
        latest_message = messages.last() if messages else None
        
        # Check for unread messages in the conversation
        unread_count = messages.filter(is_read=False).exclude(sender=user).count()

        conversation_list.append({
            'conversation': conversation,
            'latest_message': latest_message,
            'unread_count': unread_count,
        })

    context = {
        'conversations': conversation_list,
        'unread_notifications_count': unread_notifications_count,
    }
    return render(request, 'chat/conversation.html', context)



def get_unread_notifications(request):
    """Fetch all unread notifications for the current user."""
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, read=False)
        return render(request, 'notifications/view_conversation_popup.html', {'unread_notifications': unread_notifications})
    return redirect('login')  # Redirect to login if the user is not authenticated