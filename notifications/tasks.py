from .models import Notification,UserNotificationsSetting
from siteinfo.systemsendmail import send_quick_mail
from accaunts.models import UserAuthentication
from django.contrib.auth.models import User
from sellers.models import Seller
from celery import shared_task
from accaunts.models import NationalIDAuthentication



@shared_task
def start_sent_notifications():
    print('-start_sent_notifications')
    for notf in Notification.objects.all(): 
        send_notification(notf.pk,notf.notification_for)



@shared_task
def start_runing_functions():
    print('- start_runing_functions')
    
    from .shop_notification import (
        notification_followers_count,
        notification_of_collected_reservs,
        unresponsed_questions,
        notification_on_unavailable_product,
        notification_product_quant_in_carts,
        notification_in_birthday_and_sent_random_coupon,
        cart_product_is_running_out
    )
    
    notification_of_collected_reservs()
    unresponsed_questions()
    notification_followers_count()
    notification_on_unavailable_product()
    notification_product_quant_in_carts()
    notification_in_birthday_and_sent_random_coupon()
    cart_product_is_running_out()



def send_notification(notification_id,send_notification_for):
    
    from .views import get_or_create_user_notification
    for user in User.objects.all():
        try:
            user_notification_setting = UserNotificationsSetting.objects.get(
                user = user
            )
        except UserNotificationsSetting.DoesNotExist:
            user_notification_setting = UserNotificationsSetting.objects.create(
                user = user
            )
 

            if send_notification_for == 'public':
                if user_notification_setting.sent_notify_to_site == True:
                    user_notf = get_or_create_user_notification(user,notification_id=notification_id)

                if user_notification_setting.sent_notify_to_email == True:
                    if user_notf.is_sent == False:
                        send_quick_mail(
                            subject='',
                            message='',
                            to_email=user.email,
                        )                
                        user_notf.is_sent = True
                        user_notf.save()

            elif send_notification_for == 'user_authentication':
                try:
                    UserAuthentication.objects.get(
                        user = user
                    )
                    if user_notification_setting.sent_notify_to_email == True:
                        send_quick_mail(
                            subject='',
                            message='',
                            to_email=user.email,
                        )   
                    if user_notification_setting.sent_notify_to_site == True:
                        get_or_create_user_notification(user,notification_id=notification_id)
                except UserAuthentication.DoesNotExist:
                    pass
            # elif send_notification_for == 'nation_id_cart':
            #     try:
            #         NationalIDAuthentication.objects.get(
            #             user = user
            #         )
            #         if user_notification_setting.sent_notify_to_email == True:
            #             send_quick_mail(
            #                 subject='',
            #                 message='',
            #                 to_email=user.email,
            #             )  
            #         if user_notification_setting.sent_notify_to_site == True:
            #             get_or_create_user_notification(user,notification_id=notification_id)
            #     except NationalIDAuthentication.DoesNotExist:
            #         pass
            elif send_notification_for == 'seller':
                try:
                    Seller.objects.get(
                        user = user
                    )
                    if user_notification_setting.sent_notify_to_email == True:                            
                        send_quick_mail(
                            subject='',
                            message='',
                            to_email=user.email,
                        )  
                    if user_notification_setting.sent_notify_to_site == True:
                        get_or_create_user_notification(user,notification_id=notification_id)
                except Seller.DoesNotExist:
                    pass
