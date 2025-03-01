from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.

from django.shortcuts import get_object_or_404, redirect
from .models import Notification

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)

    # Mark the notification as read
    notification.read = True
    notification.save()

    # Redirect to the appropriate page (you can customize this)
    return redirect(notification.url)  # Redirect to the notification URL


def get_unread_notifications(request):
    """Fetch all unread notifications for the current user."""
    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(recipient=request.user, read=False)
        return render(request, 'notifications/unread_notifications.html', {'unread_notifications': unread_notifications})
    return redirect('login')  # Redirect to login if the user is not authenticated



def mark_all_as_read(request):
    """Marks all notifications for the current user as read."""
    if request.user.is_authenticated:
        # Mark all notifications as read for the current user
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return redirect('notifications:list')  # Redirect to the notifications list or another page


def mark_all_as_read(request):
    """Marks all notifications for the current user as read."""
    if request.user.is_authenticated:
        # Mark all notifications as read for the current user
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
    return redirect('notifications:list')  # Redirect to the notifications list or another page



def list_notifications(request):
    """List all notifications for the current user."""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
        return render(request, 'notifications/list.html', {'notifications': notifications})
    return redirect('login')



def notifications_view(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(recipient=request.user, read=False).order_by('-created_at')
    else:
        notifications = []

    context = {
        'notifications': notifications,
    }
    return render(request, 'chat/view_conversation_popup.html', context)