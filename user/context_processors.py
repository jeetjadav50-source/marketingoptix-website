from .models import Message, Notification, User

def unread_counts(request):
    if request.session.get("uid"):
        uid = request.session.get("uid")
        user_obj = User.objects.filter(userid=uid).first()
        unread_messages = Message.objects.filter(receiver_id=uid, is_read=False).count()
        unread_notifications = Notification.objects.filter(userid_id=uid, is_read=False).count()
        return {
            'global_unread_messages': unread_messages,
            'global_unread_notifications': unread_notifications,
            'user_obj': user_obj
        }
    return {
        'global_unread_messages': 0,
        'global_unread_notifications': 0,
        'user_obj': None
    }
