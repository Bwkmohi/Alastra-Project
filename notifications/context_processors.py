
from .models import UserNotification
from accaunts.check_auth import check_user


def unseenNotificaton_context(request):
    user=check_user(request)
    if not user:
        return {'un_seen_notf':0}
        
    list_unseen_notiifcations = []
    for notification in UserNotification.objects.filter(user = user):
        list_unseen_notiifcations.append(
            notification.count_unseen_notifications()
        )
        
    return {
        'un_seen_notf':sum(
            list_unseen_notiifcations
        )
    }