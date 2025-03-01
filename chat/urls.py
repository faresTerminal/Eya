from django.urls import path
from . import views

urlpatterns = [
    path('start-conversation/<int:product_id>/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:conversation_id>/', views.view_conversation, name='view_conversation'),
    # URL for displaying seller's conversations
    path('conversations/', views.conversation_list_view, name='conversation_list'),
]
