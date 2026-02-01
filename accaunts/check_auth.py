from django.contrib.auth.models import User
from .models import UserAuthentication,NationalIDAuthentication
from django.contrib.sessions.models import Session


def check_user(request):
    user_id = request.user.pk

    if user_id:
        try:
            return User.objects.get(id = user_id,is_staff = True,is_active=True) 
        except User.DoesNotExist:
            return None
    return None
    

def check_user_authentication(request):
    try:
        return UserAuthentication .objects.get(
            user__id = request.user.pk
        )
    except UserAuthentication.DoesNotExist:
        return False       


def check_nation_cart(request):
    user = check_user(request)

    if user:
        try:
            return NationalIDAuthentication.objects.get(
                user = user
            ) 
        except NationalIDAuthentication.DoesNotExist:
            return None
    
    return None