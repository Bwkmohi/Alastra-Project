from django.contrib import messages
from sellers.models import Seller
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from accaunts.check_auth import check_user
from .models import UserNotification,Notification,UserNotificationsSetting
from django.shortcuts import  redirect, render
from django.http import JsonResponse
from .tasks import start_sent_notifications



def notifications_list(request):
    user = check_user(request)
    start_sent_notifications()
    user_notf_setting=get_or_create_notification_setting(request.user) 
    notifications = UserNotification.objects.filter(user=user).order_by(
        '-created'
    )
    get_or_create_notification_setting(request.user)

    if not user:
        return redirect('acc:login')
    
    if user_notf_setting.sent_notify_to_site == False:
        messages.info(
            request,
            'برای دریافت اعلان ها و اعلان ها را روشن کنید'
        )
        return render(
            request,
            'notifications/notifications_list.html',
        )
    
    if request.method == 'POST':
        query = UserNotification.objects.filter
        filter_q = request.POST.get('filter_q')

        if filter_q == 'is_read':
            notifications = query(
                notification__user = user,
                is_read = True
            )

        elif filter_q == 'is_not_read':
            notifications = query(
               notification__user = user,
                is_read = False
            )

        elif filter_q == 'all':
            notifications = query(
                notification__user = user,
                notification__for_all_users = True
            ) 

        return render(
            request,
            'notifications/notifications_list.html',
            {
                'notify':notifications.distinct()
            }
        )
    else:
        notifications.update(is_read=True)
        return render(
            request,
            'notifications/notifications_list.html',{
            'notify':notifications
        }
    )



def get_or_create_user_notification(user,notification_id):
    notification = get_object_or_404(
        Notification,id =notification_id
    )
    try:
        return UserNotification.objects.get(
            notification = notification,
            user = user
        )
    except UserNotification.DoesNotExist:
        return UserNotification.objects.create(
            notification = notification,
            user = user
        )

        

def close_or_open_email_notifications(request):
    setting = get_or_create_notification_setting(request.user)

    if setting.sent_notify_to_email == False:
        setting.sent_notify_to_email = True
        setting.save()

        return JsonResponse(
            {
                'status':setting.sent_notify_to_email
            }
        )
    
    else:
        setting.sent_notify_to_email = False
        setting.save()

        return JsonResponse(
            {
                'status':setting.sent_notify_to_email
            }
        )



def close_or_open_site_notifications(request):
    setting = get_or_create_notification_setting(request.user)

    if setting.sent_notify_to_site == False:
        setting.sent_notify_to_site = True
        setting.save()

        return JsonResponse(
            {
                'status':setting.sent_notify_to_site
            }
        )

    else:
        setting.sent_notify_to_site = False
        setting.save()

        return JsonResponse(
            {
                'status':setting.sent_notify_to_site
            }
        )



def show_defult_notification_status(request):
    setting = get_or_create_notification_setting(request.user)
    return JsonResponse(
        {
            'site_ntf_stts':setting.sent_notify_to_site,
            'email_ntf_stts':setting.sent_notify_to_email
        }
    )


 
def get_or_create_notification_setting(user):
    try:
        return UserNotificationsSetting.objects.get(
            user = user
        )
    except:
        return UserNotificationsSetting.objects.create(
            user = user,
        )