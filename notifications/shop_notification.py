from shop.models import Products
from siteinfo.systemsendmail import send_quick_mail
from django.shortcuts import get_object_or_404
from .views import get_or_create_user_notification,get_or_create_notification_setting
from sellers.models import Shop
from follow.models import FolloweUnFollow
from reservations.models import Reservation
from shop.models import Comments
from cart.models import Cart
from .models import Notification
from question_response.models import Question
from collaborator.models import ShopCollaborator
from shop.models import Products
from siteinfo.systemsendmail import send_quick_mail
from .views import get_or_create_notification_setting,get_or_create_user_notification
from cart.models import Cart
from .models import Notification
from accaunts.models import UserAuthentication
from copon2.models import Coupon
from datetime import date
from django.utils import timezone




 

 
def notification_in_new_question(question_id):
    question = get_object_or_404(Question, id=question_id)
    shop = question.product.shop
    seller_user = shop.seller.user

    subject = 'سوال جدید درباره محصول شما'
    message = (
        f'سلام،\n\n'
        f'یک سوال جدید درباره محصول "{question.product.name}" در فروشگاه "{shop.name_shop}" ثبت شده است.\n'
        f'متن سوال: "{question.text}"\n\n'
        'لطفاً به پنل مدیریت فروشگاه مراجعه کرده و پاسخ مناسب را ارسال نمایید.\n'
        'با تشکر از همکاری شما.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    # ارسال نوتیفیکیشن به همکارانی که مجوز پاسخگویی دارند
    collaborators = ShopCollaborator.objects.filter(
        shop=shop,
        can_response_questions=True,
        can_see_comments_and_questions=True
    )
    for collab in collaborators:
        un = get_or_create_user_notification(collab.user, n.pk)
        un.is_sent = True
        un.save()
        if get_or_create_notification_setting(collab.user).sent_notify_to_email:
            send_quick_mail(
                subject=subject,
                message=message,
                to_email=collab.user.email
            )
    
    # ارسال نوتیفیکیشن به فروشنده اصلی فروشگاه
    un = get_or_create_user_notification(seller_user, n.pk)
    un.is_sent = True
    un.save()
    if get_or_create_notification_setting(seller_user).sent_notify_to_email:
        send_quick_mail(
            subject=subject,
            message=message,
            to_email=seller_user.email
        )



def notification_in_new_follower(shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    seller_user = shop.seller.user

    subject = 'دنبال‌کننده جدید برای فروشگاه شما'
    message = (
        f'سلام {seller_user.first_name} عزیز،\n\n'
        f'فروشگاه شما با نام "{shop.name_shop}" یک دنبال‌کننده جدید پیدا کرده است.\n'
        'با افزایش دنبال‌کننده‌ها، احتمال فروش محصولات شما بیشتر خواهد شد!\n\n'
        'با آرزوی موفقیت برای شما.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    un = get_or_create_user_notification(seller_user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(seller_user).sent_notify_to_email:
        send_quick_mail(
            subject=subject,
            message=message,
            to_email=seller_user.email
        )



def notification_in_new_comment(comment_id):
    comment = get_object_or_404(Comments, id=comment_id)
    product = comment.product
    shop = product.shop
    seller_user = shop.seller.user

    subject = 'نظر جدید درباره محصول شما'
    message = (
        f'سلام،\n\n'
        f'یک دیدگاه جدید درباره محصول "{product.name}" ثبت شده است.\n'
        f'متن نظر: "{comment.message}"\n\n'
        'لطفاً جهت بررسی و پاسخ (در صورت نیاز) به پنل فروشنده مراجعه نمایید.\n'
        'با تشکر از همکاری شما.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    # اطلاع به همکاران فروشگاه که اجازه مشاهده نظرها را دارند
    for collab in ShopCollaborator.objects.filter(
        shop=shop,
        can_see_comments_and_questions=True
    ):
        un = get_or_create_user_notification(collab.user, n.pk)
        un.is_sent = True
        un.save()

        if get_or_create_notification_setting(collab.user).sent_notify_to_email:
            send_quick_mail(
                subject,
                message,
                collab.user.email
            )

    un = get_or_create_user_notification(seller_user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(seller_user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            seller_user.email
        )



def notification_in_new_reservation(reserv_id):
    reserv = get_object_or_404(Reservation, id=reserv_id)
    shop = reserv.shop
    product = reserv.product
    order = reserv.order
    buyer = order.user

    subject = 'سفارش جدید در فروشگاه شما ثبت شد'
    message = (
        f'سلام،\n\n'
        f'یک سفارش جدید برای محصول "{product.name}" در فروشگاه "{shop.name_shop}" ثبت شده است.\n'
        f'تعداد سفارش: {reserv.quantity} عدد\n'
        f'توسط کاربر: {buyer.get_full_name() or buyer.username}\n\n'
        'لطفاً جهت پردازش و ارسال سفارش، به پنل فروشنده مراجعه نمایید.\n'
        'با تشکر.'
    )

    created = False 
    if not created:
        n = Notification.objects.create(
            subject=subject,
            message=message,
            notification_type='private',
        )
        created = True

    for collab in ShopCollaborator.objects.filter(
        shop=shop,
        can_edit_orders=True,
        can_see_orders=True
    ):
        un = get_or_create_user_notification(collab.user, n.pk)
        un.is_sent = True
        un.save()

        if get_or_create_notification_setting(collab.user).sent_notify_to_email:
            send_quick_mail(
                subject,
                message,
                collab.user.email
            )

    un = get_or_create_user_notification(shop.seller.user, n.pk)
    un.is_sent = True
    un.save()

    if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
        send_quick_mail(
            subject,
            message,
            shop.seller.user.email
        )


#  
def notification_of_collected_reservs():
    for shop in Shop.objects.filter(active=True, reported=False):
        reservations = Reservation.objects.filter(
            shop=shop,
            preparation =True,
            paid=True
        )
        if reservations.count() > 10:
            subject = 'تعداد سفارشات تحویل‌نشده بالا رفته است'
            message = (
                f'سلام،\n\n'
                f'تعداد سفارشات پرداخت شده اما تحویل‌نشده و ارسال نشده در فروشگاه "{shop.name_shop}" به بیش از ۱۰ عدد رسیده است.\n'
                f'لطفاً هر چه سریع‌تر نسبت به ارسال سفارش‌ها اقدام نمایید تا رضایت مشتریان حفظ شود.\n\n'
                'با تشکر از همکاری شما.'
            )

            created = False 
            if not created:
                n = Notification.objects.create(
                    subject=subject,
                    message=message,
                    notification_type='private',
                )
                created = True

            for collab in ShopCollaborator.objects.filter(
                shop=shop,
                can_edit_orders=True,
                can_see_orders=True
            ):
                un = get_or_create_user_notification(collab.user, n.pk)
                un.is_sent = True
                un.save()

                if get_or_create_notification_setting(collab.user).sent_notify_to_email:
                    send_quick_mail(
                        subject=subject,
                        message=message,
                        to_email=collab.user.email
                    )   

            un = get_or_create_user_notification(shop.seller.user, n.pk)
            un.is_sent = True
            un.save()

            if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
                send_quick_mail(
                    subject=subject,
                    message=message,
                    to_email=shop.seller.user.email
                )


# 
def unresponsed_questions():
    for shop in Shop.objects.filter(active=True, reported=False):
        un_responsed_questions = Question.objects.filter(product__shop__id=shop.pk, responsed=False)
        subject = 'هشدار: سوالات بی‌پاسخ بیش از حد'
        message = f'سلام، فروشگاه شما بیش از ۵ سوال بی‌پاسخ دارد. لطفاً هرچه سریع‌تر به سوالات کاربران پاسخ دهید تا رضایت مشتریان حفظ شود.'

        if un_responsed_questions.count() > 5:
            
            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )

            for collab in ShopCollaborator.objects.filter(shop=shop, can_response_questions=True, can_see_comments_and_questions=True):
                
                un = get_or_create_user_notification(collab.user, n.pk)
                un.is_sent = True
                un.save()

                if get_or_create_notification_setting(collab.user).sent_notify_to_email:
                    send_quick_mail(
                        subject,
                        message,
                        collab.user.email
                    )   

            un = get_or_create_user_notification(shop.seller.user, n.pk)
            un.is_sent = True
            un.save()

            if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
                send_quick_mail(
                    subject,
                    message,
                    shop.seller.user.email
                )


# 
def notification_followers_count():
    milestones = [250, 500, 700, 1000]
    for shop in Shop.objects.filter(active=True, reported=False):
        followers_count = FolloweUnFollow.objects.filter(shop__id=shop.pk).count()

        # بررسی اینکه آیا تعداد دنبال‌کننده‌ها به یکی از حد نصاب‌ها رسیده
        if followers_count in milestones:
            subject = 'تبریک! تعداد دنبال‌کنندگان شما افزایش یافته است'
            message = f'سلام، فروشگاه شما اکنون {followers_count} دنبال‌کننده دارد. این موفقیت را به شما تبریک می‌گوییم!'

            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )

            un = get_or_create_user_notification(shop.seller.user, n.pk)
            un.is_sent = True
            un.save()

            if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
                send_quick_mail(
                    subject=subject,
                    message=message,
                    to_email=shop.seller.user.email
                )


# 
def notification_on_unavailable_product():
    for shop in Shop.objects.filter(active=True, reported=False):
        for product in Products.objects.filter(shop__id=shop.pk, active=True):
            if product.qunat if product.qunat else 0 < 2:
                
                subject = 'هشدار: محصول ناموجود یا نزدیک به اتمام موجودی'
                message = f'سلام، موجودی محصول "{product.name}" در فروشگاه شما کم است یا تمام شده است. لطفاً جهت تامین موجودی اقدام کنید.'

                n = Notification.objects.create(
                    subject=subject,
                    message=message,
                    notification_type='private',
                )

                for collab in ShopCollaborator.objects.filter(shop=shop, can_response_questions=True, can_see_comments_and_questions=True):
                    un = get_or_create_user_notification(collab.user, n.pk)
                    un.is_sent = True
                    un.save()

                    if get_or_create_notification_setting(collab.user).sent_notify_to_email:
                        send_quick_mail(
                            subject,
                            message,
                            collab.user.email
                        )

                un = get_or_create_user_notification(shop.seller.user, n.pk)
                un.is_sent = True
                un.save()

                if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
                    send_quick_mail(
                        subject,
                        message,
                        shop.seller.user.email
                    )


# 
def notification_product_quant_in_carts():
    for shop in Shop.objects.all():
        carts = Cart.objects.filter(product__shop__id=shop.pk)

        if carts.count() > 50:
            subject = 'هشدار: تعداد بالای محصولات در سبد خرید کاربران'
            message = f'سلام، بیش از 50 محصول از فروشگاه شما در سبد خرید کاربران قرار گرفته است. این موضوع می‌تواند نشانه‌ای از علاقه بالا به محصولات باشد. لطفاً وضعیت موجودی و قیمت‌ها را بررسی کنید.'

            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )

            un = get_or_create_user_notification(
                shop.seller.user,
                n.pk
            )
            un.is_sent = True
            un.save()

            if get_or_create_notification_setting(shop.seller.user).sent_notify_to_email:
                send_quick_mail(
                    subject=subject,
                    message=message,
                    to_email=shop.seller.user.email
                )
      

# 
def notification_in_birthday_and_sent_random_coupon():
    today = date.today()

    # گرفتن کوپن فعال و معتبر (مثلاً اولین کوپن فعال)
    valid_coupons = Coupon.objects.filter(
        active=True,
        valid_from__lte=timezone.now(),
    ).filter(
        valid_to__gte=timezone.now(),
        active = True
    )

    if not valid_coupons.exists():
        print("کوپن فعال معتبر موجود نیست!")
        return

    coupon = valid_coupons.first()  

    users = UserAuthentication.objects.all()

    for user_auth in users:
        birth_date = user_auth.age  
        if birth_date.month == today.month and birth_date.day == today.day:
            user = user_auth.user
 
            subject = "تولد مبارک! کوپن هدیه برای شما"
            message = f"""
            سلام {user.username} عزیز،

            تولدتون مبارک! ما یک کوپن هدیه برای شما آماده کرده‌ایم.

            کد کوپن شما: {coupon.code}

            لطفا از آن استفاده کنید و روز خوبی داشته باشید!
            """

            send_quick_mail(subject, message, user.email)


#  
def cart_product_is_running_out():
    products = Products.objects.filter(
       qunat__lte=1 
    )
    carts = Cart.objects.filter(
        product__id__in=products
    )
    for cart in carts:
        subject = 'هشدار: موجودی محصول در حال اتمام است'
        message = f'سلام {cart.user.first_name} عزیز، موجودی محصول "{cart.product.name}" که در سبد خرید شما قرار دارد بسیار کم شده است. لطفاً در صورت تمایل هرچه سریع‌تر خرید خود را نهایی کنید.'
        created = False 
        if not created:
            n = Notification.objects.create(
                subject=subject,
                message=message,
                notification_type='private',
            )
            created = True
        un = get_or_create_user_notification(cart.user, n.pk)
        un.is_sent = True
        un.save()

        if get_or_create_notification_setting(cart.user).sent_notify_to_email:
            send_quick_mail(
                subject=subject,
                message=message,
                to_email=cart.user.email
            )
