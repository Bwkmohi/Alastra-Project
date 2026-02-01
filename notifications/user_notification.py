from shop.models import Products
from watchlist.models import WatchList
from siteinfo.systemsendmail import send_quick_mail
from django.shortcuts import get_object_or_404
from follow.models import FolloweUnFollow
from .views import get_or_create_notification_setting,get_or_create_user_notification
from sellers.models import Shop
from story.models import Story
from reservations.models import Reservation,OrderModel
from .models import Notification
from question_response.models import Question
from tiketing.models import ResponseToTiket
from walet.models import Transaction,Wallet
from django.urls import reverse
from config import settings
from group_cart.models import GroupCart
from chat.models import Message
 

 
def notification_in_add_product(product_id,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)
    product = get_object_or_404(Products,id =product_id)
    
    

    for users in FolloweUnFollow.objects.filter(shop__id = shop.pk):
        user_notification_setting = get_or_create_notification_setting(users.user)    
        subject = 'محصول جدید افزوده شد!'
        message = f'فروشگاه {shop.name_shop} محصول {product.name} - ({product.price}) را اضافه کرد'

        created = False 
        if not created:
            n=Notification.objects.create(
                subject = subject,
                message = message,
                notification_type = 'private',
            )
            created = True

        un=get_or_create_user_notification(users.user,n.pk)    
        un.is_sent= True
        un.save()

        

        if user_notification_setting.sent_notify_to_email == True:
            send_quick_mail(
                subject=subject,
                message=message,
                to_email = users.user.email
            )


 
def notification_in_add_story(story_id,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)
    story = Story.objects.get(id = story_id)
    for users in FolloweUnFollow.objects.filter(shop__id = shop.pk):

        subject = f"داستان جدید در فروشگاه {shop.name_shop} اضافه شد"
        message = f"داستانی در فروشگاه {shop.name_shop} اضافه گردید."

        created = False 
        if not created:
            n=Notification.objects.create(
                subject = subject,
                message = message,
                notification_type = 'private',
            )
            created = True

        un=get_or_create_user_notification(users.user,n.pk)
        un.is_sent= True
        un.save()

        if get_or_create_notification_setting(users.user).sent_notify_to_email == True:
            send_quick_mail(
                subject=subject,
                message=message,
                to_email = users.user.email
            )


 
def notification_in_edit_product_price_or_sell_price(product_id, shop_id, activti_type):
    product = get_object_or_404(Products, id=product_id)
    shop = get_object_or_404(Shop, id=shop_id)
    created = False

    for users in WatchList.objects.filter(product = product):
        if activti_type == 'edit_price':
            subject = f"اعلان واچ لیست!"
            message = f"قیمت محصول '{product.name}' در فروشگاه {shop.name_shop} به‌روزرسانی شد."
        elif activti_type == 'edit_sell_price':
            subject = f"اعلان واچ لیست!"
            message = f"قیمت محصول '{product.name}' در فروشگاه {shop.name_shop} کاهش یافت ."

        if not created:
            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )
            created = True

        un = get_or_create_user_notification(users.user, n.pk)
        un.is_sent = True
        un.save()

        if get_or_create_notification_setting(users.user).sent_notify_to_email == True:
            send_quick_mail(
                subject=subject,
                message=message,
                to_email=users.user.email
            )


 
def your_question_has_been_responsed(question_id, response_id):
    question = get_object_or_404(Question, id=question_id)

    subject = 'پاسخ به سوال شما'
    message = f'  پاسخ جدیدی به سوال شما اضافه شد. '

    n=Notification.objects.create(
        subject=subject,
        message=message,
        notification_type='private',
    )

    un = get_or_create_user_notification(question.user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(question.user).sent_notify_to_email == True:
        send_quick_mail(
            subject=subject,
            message=message,
            to_email=question.user.email
        )


 
def notification_in_signup(user):
    subject = 'خوش آمدید به سایت ما!'
    message = f'سلام {user.first_name} عزیز،\n\nاز ثبت نام شما در سایت ما بسیار خوشحالیم. امیدواریم بهترین تجربه را داشته باشید.'

    created = False 
    if not created:
        n=Notification.objects.create(
            subject = subject,
            message = message,
            notification_type = 'private',
        )
        created = True
        
    un=get_or_create_user_notification(user,n.pk)
    un.is_sent= True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_site == True:
        send_quick_mail(
            subject=subject,
            message=message,
            to_email=user.email
        )


 
def reserv_status(reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    user = reservation.order.user
    
    #  تعریف پیام‌ها بر اساس وضعیت رزرو
    if reservation.canceled:
        subject = 'لغو سفارش  '
        message = f'سلام {user.first_name} عزیز،\n\nسفارش شماره {reservation.id} توسط شما لغو شده است. در صورت نیاز به راهنمایی با ما تماس بگیرید.'

    elif reservation.delivered == True:
        subject = 'سفارش شما تحویل داده شد'
        message = f'سلام {user.first_name} عزیز،\n\nسفارش شماره {reservation.id} با موفقیت تحویل شما داده شد. ممنون از اعتماد شما.'
    elif reservation.sent_to_post == True:
        subject = 'سفارش شما ارسال شد'
        message = f'سلام {user.first_name} عزیز،\n\nسفارش شماره {reservation.id} ارسال شده است. کد رهگیری: {reservation.tracking_code or "ندارد"}.'
    elif reservation.preparation == True:
        subject = 'سفارش شما بررسی شد'
        message = f'سلام {user.first_name} عزیز،\n\nسفارش شماره {reservation.id} بررسی و در حال پردازش است.'
    else:
        subject = 'به‌روزرسانی وضعیت سفارش'
        message = f'سلام {user.first_name} عزیز،\n\nوضعیت سفارش شماره {reservation.id} به‌روزرسانی شد. برای اطلاعات بیشتر وارد حساب کاربری خود شوید.'
    
    created = False
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            user.email
        )



def notification_in_deposin_to_wallet(transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    user = transaction.wallet.user.user
    
    subject = 'واریز به کیف پول شما'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        f'مبلغ {transaction.amount} تومان به کیف پول شما با شماره تراکنش {transaction_id} واریز شد.\n'
        'شما می‌توانید از این مبلغ در خریدهای بعدی خود استفاده کنید.\n\n'
        'با تشکر از همراهی شما.'
    )
    
    created = False
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            user.email
        )



def notification_in_withdrawal_from_wallet(transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    user = transaction.wallet.user.user
    
    subject = 'برداشت از کیف پول شما'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        f'مبلغ {transaction.amount} تومان از کیف پول شما با شماره تراکنش {transaction_id} برداشت شد.\n'
        'اگر این عملیات توسط شما انجام نشده، لطفاً سریعاً با پشتیبانی تماس بگیرید.\n\n'
        'با احترام.'
    )
    
    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_site:
        send_quick_mail(
            subject,
            message,
            user.email
        )


 
def paid_successful(order_id): 
    order = get_object_or_404(OrderModel, id=order_id)
    user = order.user

    subject = 'پرداخت شما با موفقیت انجام شد'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        f'پرداخت سفارش شما به شماره {order_id} با موفقیت انجام شد.\n'
        f'مبلغ پرداختی: {order.total_price} تومان\n'
        f'روش پرداخت: {order.payment_method}\n\n'
        'سفارش شما در حال پردازش است و به‌زودی ارسال خواهد شد.\n'
        'با تشکر از خرید شما.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_email:    
        send_quick_mail(
            subject,
            message,
            user.email
        )


 
def paid_faild(order_id):
    order = get_object_or_404(OrderModel, id=order_id)
    user = order.user

    subject = 'پرداخت شما ناموفق بود'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        f'پرداخت سفارش شما به شماره {order_id} با خطا مواجه شد و تکمیل نگردید.\n'
        'لطفاً مجدداً تلاش کنید یا در صورت بروز مشکل با پشتیبانی تماس بگیرید.\n\n'
        'با سپاس از همراهی شما.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            user.email
        )


 
def notification_in_answered_ticket(reseponsed_tiket_id):
    responsed_tiket = get_object_or_404(ResponseToTiket, id=reseponsed_tiket_id)
    user = responsed_tiket.response_for_user.user

    subject = 'پاسخ جدید به تیکت شما'
    message = (
        f'سلام {user.first_name} عزیز،\n\n'
        'پاسخی به تیکت پشتیبانی شما ثبت شده است.\n'
        'برای مشاهده پاسخ، لطفاً به حساب کاربری خود وارد شوید و به بخش پشتیبانی مراجعه کنید.\n\n'
        'با احترام.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True
        
    un = get_or_create_user_notification(user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            user.email
        )


 
def notification_in_payment_with_wallet(from_wallet_id, to_wallet_id, amount):
    from_wallet = get_object_or_404(Wallet, id=from_wallet_id)
    to_wallet = get_object_or_404(Wallet, id=to_wallet_id)

    user_from = from_wallet.user.user
    user_to = to_wallet.user.user

    #  موضوع و پیام برای فرستنده (کسی که مبلغ رو انتقال داده)
    subject_user1 = 'تراکنش موفق در کیف پول شما'
    message_user1 = (
        f'سلام {user_from.first_name} عزیز،\n\n'
        f'مبلغ {amount} تومان با موفقیت از کیف پول شما به کیف پول کاربر {user_to.get_full_name() or user_to.username} انتقال یافت.\n'
        'با تشکر از استفاده شما از خدمات ما.'
    )

    # موضوع و پیام برای گیرنده (کسی که مبلغ به کیف پولش واریز شده)
    subject_user2 = 'واریز وجه به کیف پول شما'
    message_user2 = (
        f'سلام {user_to.first_name} عزیز،\n\n'
        f'مبلغ {amount} تومان به کیف پول شما از طرف کاربر {user_from.get_full_name() or user_from.username} واریز شد.\n'
        'لطفاً برای مشاهده جزئیات به حساب کاربری خود مراجعه کنید.'
    )

    created = False 
    if not created:
        # نوتیفیکیشن برای فرستنده
        n1 = Notification.objects.create(
            subject=subject_user1,
            message=message_user1,
            notification_type='private',
        )
        # نوتیفیکیشن برای گیرنده
        n2 = Notification.objects.create(
            subject=subject_user2,
            message=message_user2,
            notification_type='private',
        )
        created = True

    # ثبت نوتیفیکیشن فرستنده
    un1 = get_or_create_user_notification(user_from, n1.pk)
    un1.is_sent = True
    un1.save()

    # ثبت نوتیفیکیشن گیرنده
    un2 = get_or_create_user_notification(user_to, n2.pk)
    un2.is_sent = True
    un2.save()

    # ارسال ایمیل به فرستنده اگر فعال باشد
    if get_or_create_notification_setting(user_from).sent_notify_to_email:
        send_quick_mail(
            subject_user1,
            message_user1,
            user_from.email
        )

    # ارسال ایمیل به گیرنده اگر فعال باشد
    if get_or_create_notification_setting(user_to).sent_notify_to_email:
        send_quick_mail(
            subject_user2,
            message_user2,
            user_to.email
        )



def notification_in_reserv_with_group_cart(group_id):
    group = get_object_or_404(GroupCart, id=group_id)

    for user in group.users.all():

        relative_url = reverse('group_c:get_export_from_cart', kwargs={'group_id': group.id})
        full_url = f'<a href="{settings.SITE_DOMAIN}{relative_url}">{settings.SITE_DOMAIN}{relative_url}<a>'
        subject = 'لینک خروجی سبد گروهی شما'
        message = f'سلام {user.username}،\n\nبرای دیدن سبد گروهی خود لطفا روی لینک زیر کلیک کنید:\n{full_url}'

        created = False 
        if not created:
            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )
            created = True

        un = get_or_create_user_notification(user, n.pk)
        un.is_sent = True
        un.save()

        if get_or_create_notification_setting(user).sent_notify_to_email:
            send_quick_mail(
                subject,
                message,
                user.email
            )


 
def you_have_new_message(message_id):
    message_model = Message.objects.get(id=message_id, seen=False)
    
    subject = 'پیام جدید برای شما'
    message = f'سلام {message_model.receiver.first_name} عزیز، شما یک پیام جدید از طرف {message_model.sender.first_name} دریافت کرده‌اید. لطفاً برای مشاهده پیام به سایت مراجعه کنید.'
    
    if get_or_create_notification_setting(message_model.receiver).sent_notify_to_site == True:
        send_quick_mail(
            subject=subject,
            message=message,
            to_email=message_model.receiver.email
        )
