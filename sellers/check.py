from .models import Seller,Shop
from accaunts.check_auth import check_user,check_user_authentication



def check_is_seller(request):
    user = check_user(request)
    user_authentication = check_user_authentication(request)
    # national_id_auth=check_nation_cart(request)

    if not user:return None

    if not user_authentication:return None
    
    # if not national_id_auth:return None
    # national_id_auth=national_id_auth,
    try:
        return Seller.objects.get(user = user,user_authentication = user_authentication,is_seller = True,is_active = True
        )
    except Seller.DoesNotExist:
        return None



def get_shop(request,shop_id):
    try:
        return Shop.objects.get(id=shop_id,active=True,reported=False)
    except Shop.DoesNotExist:
        return None



def check_seller_shop(request,shop_id):
    seller = check_is_seller(request)
    if not seller:
        return None
    try:
        return Shop.objects.get(seller = seller,id = shop_id,reported=False)
    except Shop.DoesNotExist:
        return None