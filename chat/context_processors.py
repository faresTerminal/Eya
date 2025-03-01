from .models import Conversation

def user_conversations(request):
    if request.user.is_authenticated:
        conversations = Conversation.objects.filter(
            seller=request.user
        ).select_related('buyer').union(
            Conversation.objects.filter(buyer=request.user).select_related('seller')
        )
        return {'conversations': conversations}
    return {}
