from .models import Wallet
from accaunts.check_auth import check_user_authentication



def wallet_balance(request):
    user = check_user_authentication(request)

    if not user:
        return {'balance':0}
    
    try:
        return {'balance':Wallet.objects.get(user = user).balance}
    except Wallet.DoesNotExist:
        return {
            'balance':0
        }