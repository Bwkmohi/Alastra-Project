from .models import Shop ,Seller
from accaunts.check_auth import check_user



def default_shop_context(request):
    user = check_user(request)
    
    if not user:return {}
    try:
         if request.resolver_match:
            shop_id = request.resolver_match.kwargs.get('shop_id')
            if shop_id:
                try:
                    shop = Shop.objects.get(seller__is_seller=True,id=shop_id,reported=False,active=True)
                    return {'shop_id': shop.id}
                except Shop.DoesNotExist:
                    pass
            else:pass
    except Exception as e:
        print(f"Error in default_shop_context: {e}")
    return {}



def shop_context(request):
    shop_id = request.session.get('shop_id')
    if not shop_id:
        return {}

    try:
        shop = Shop.objects.get(id=shop_id)
        return {'shop_data': shop}
    except Shop.DoesNotExist:
        return {}



def is_seller_context(request):
    user = check_user(request)

    try:
        seller_user = Seller.objects.get(
            user = user,
            is_seller = True,
            is_active = True
        )
        return {
            'is_seller': seller_user
        }
    except Seller.DoesNotExist:
        return {}