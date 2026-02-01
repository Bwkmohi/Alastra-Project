from .models import Cart
from accaunts.check_auth import check_user

def quantityCart(request):
    user = check_user(request)
    if user:
        for item in Cart.objects.filter(user=user):  
            if item.cart_quantity():
                return {'qty':item.cart_quantity()}
            else:
                return {'qty':0}                 
    return {}