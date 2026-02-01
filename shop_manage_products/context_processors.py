from shop.models import Products
from sellers.context_processors import default_shop_context


def count_shop_products(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_products':Products.objects.filter(shop__id = shop_id,active = True).count()
    }


def count_shop_lte2_products(request):
    shop_id = default_shop_context(request).get('shop_id')
    return {
        'count_shop_lte2_products':Products.objects.filter(shop__id = shop_id,active = True,qunat__lte=2).count()
    }
