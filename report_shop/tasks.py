from sellers.models import Shop
from .models import ReportShop
from django.core.mail import send_mail
from config.settings import ADMIN_GMAIL
from celery import shared_task
from shop.models import Products

@shared_task
def report_counts():
    print('- Startted Report Shops!!!')
    shops_to_update = []
    for i in Shop.objects.filter(active=True, reported=False):
        shops_with_reports = ReportShop.objects.filter(is_true=True, shop=i)
        if shops_with_reports.count() > 12:
            i.reported = True
            i.active = False
            Products.objects.filter(shop = i,active = True).update(active = False)
            shops_to_update.append(i)
            send_mail(
                'report',
                f'حساب فروشگاه {i.name_shop} شما به دلیل گزارشات متعدد مسدود شد!',
                ADMIN_GMAIL,
                [i.seller.user.email]
            )
    
    Shop.objects.bulk_update(shops_to_update, ['reported'])
