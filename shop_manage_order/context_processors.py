from sellers.context_processors import default_shop_context
from reservations.models import Reservation
from django.utils import timezone
from datetime import datetime, time



def count_shop_paid_reservs(request):
    return {
        'count_shop_paid_reservs':Reservation.objects.filter(
            shop__id = default_shop_context(request).get('shop_id'),
            order__paid = True,
            paid = True
        ).count()
    }



def count_shop_send_reservs(request):
    return {
        'count_shop_send_reservs':Reservation.objects.filter(
            shop__id = default_shop_context(request).get('shop_id'),
            order__paid = True,
            paid = True,
            sent_to_post = True,
        ).count()
    }



def count_shop_unsend_reservs(request):
    return {
        'count_shop_unsend_reservs':Reservation.objects.filter(
            shop__id = default_shop_context(request).get('shop_id'),
            order__paid = True,
            paid = True,
            sent_to_post = False
        ).count()
    }



def count_shop_canceled_reservs(request):
    return {
        'count_shop_canceled_reservs':Reservation.objects.filter(
            canceled=True,
            shop__id = default_shop_context(request).get('shop_id'),
            order__paid = True,
            paid = True,
        ).count()
    }



def count_shop_today_reservs(request):
    start_of_day = timezone.make_aware(datetime.combine(timezone.now().date(), time.min))
    end_of_day = timezone.make_aware(datetime.combine(timezone.now().date(), time.max))
    return {
        'count_shop_today_reservs':Reservation.objects.filter(
            shop__id = default_shop_context(request).get('shop_id'),
            order__paid = True,
            paid = True,
            order__created_at__gte=start_of_day, 
            order__created_at__lte=end_of_day
           
        ).count()
    }