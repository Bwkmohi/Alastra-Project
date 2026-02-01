from reservations.models import Reservation
from django.utils import timezone
from .models import MonthlyProfit, ProductPriceHistory
from django.apps import apps
from shop.models import Products
from django.db.models import Sum
from celery import shared_task

@shared_task
def monthly_job():
    now = timezone.now()
    current_month = now.month
    current_year = now.year

    reservations = (
        Reservation.objects
        .filter(
            paid=True,
            order__created_at__month=current_month,
            order__created_at__year=current_year
        )
        .values('shop')
        .annotate(total_profit=Sum('totalprice'))
    )

    for item in reservations:
        obj = MonthlyProfit.objects.filter(
            shop_id=item['shop'],
            year=current_year,
            month=current_month
        ).first()

        if obj:
            obj.total_profit = item['total_profit']
            obj.save()
        else:
            MonthlyProfit.objects.create(
                shop_id=item['shop'],
                year=current_year,
                month=current_month,
                total_profit=item['total_profit']
            )

    return "تمام سودهای ماهانه ذخیره شد."


@shared_task
def monthly_price_history_job():
    print(" ثبت قیمت محصولات برای ماه جاری آغاز شد...")

    now = timezone.now()
    current_year = now.year
    current_month = now.month
    Shop = apps.get_model('sellers', 'Shop')

    for shop in Shop.objects.all():
        for product in Products.objects.all():
            try:
                existing = ProductPriceHistory.objects.filter(
                    product=product,
                    shop=shop,
                    date__year=current_year,
                    date__month=current_month
                ).exists()

                if not existing:
                    price = product.price  
                    ProductPriceHistory.objects.create(
                        product=product,
                        shop=shop,
                        price=price,
                        date=now.date()
                    )
                    print(f" قیمت {product.name} برای کانال {shop.name_shop} ذخیره شد: {price}")
                else:
                    print(f" قیمت {product.name} برای کانال {shop.name_shop} در ماه جاری قبلاً ثبت شده.")

            except Exception as e:
                print(f" خطا در ثبت قیمت {product.name} برای کانال {shop.name_shop}: {e}")
