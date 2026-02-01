from copon2.models import Coupon
from sellers.context_processors import default_shop_context


def count_shop_coupons_context(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_coupons':Coupon.objects.filter(shop__id = shop_id).count()
    }