from django.urls import path
from . import views

app_name = 'notification'

urlpatterns = [
    #path('read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
    path('notification/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('unread/', views.get_unread_notifications, name='unread_notifications'),
    path('mark-all/', views.mark_all_as_read, name='mark_all_as_read'),
    path('list/', views.list_notifications, name='list'),
]
