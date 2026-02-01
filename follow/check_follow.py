from.models import FolloweUnFollow

def checkFollow(request,shop_id,user_id):
    try:
        FolloweUnFollow.objects.get(shop__id = shop_id,user__id = user_id)
        return True
    except FolloweUnFollow.DoesNotExist:
        return False