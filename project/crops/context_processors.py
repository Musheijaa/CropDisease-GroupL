from .models import SystemMessage
from django.contrib.auth.models import User
from django.db.models import Q

def notifications(request):
    if not request.user.is_authenticated:
        return {}
    
    # Get both personal messages AND broadcasts (where user=None)
    messages = SystemMessage.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('-created_at')
    
    return {
        'unread_count': messages.filter(is_read=False).count(),
        'user_messages': messages[:5]  # Show 5 most recent
    }