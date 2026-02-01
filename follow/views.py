from django.shortcuts import render,get_object_or_404,redirect
from sellers.models import Shop
from.models import FolloweUnFollow
from django.contrib import messages
from .check_follow import checkFollow
from accaunts.check_auth import check_user
from django.http import JsonResponse
from notifications.shop_notification import notification_in_new_follower



def follow(request):
    user = check_user(request)

    if not user:
        messages.info(
            request, 
            'برای فالو کردن  لطفا ابتدا برای خود حساب باز کنید!'
        )
        return redirect('acc:login')

    if request.method == 'POST':
        shop_id = request.POST.get('shop_id')
        url = request.POST.get('url')

        user_following = checkFollow(request, shop_id=shop_id, user_id=user.pk)

        # اگر کاربر فالو میکرد . انفالو بشه 
        if user_following == True:

            try:
                FolloweUnFollow.objects.get(shop__id=shop_id, user=user).delete()
                messages.success(
                    request,
                    'با موفقیت انفالو شد!'
                )
                return redirect(url)
            except FolloweUnFollow.DoesNotExist:
                pass



        # اگر کاربر فالو نمیکرد فالو بشه
        if user_following == False:

            shop = get_object_or_404(Shop, id=shop_id)
            try:
                F=FolloweUnFollow.objects.create(shop=shop, user=user)
                messages.success(
                    request,
                    f'الان شما {F.shop.name_shop} را فالو میکنید '
                )

                notification_in_new_follower(shop_id)
                return redirect(url)
            except FolloweUnFollow.DoesNotExist:
                pass


        else:
            messages.error(
                request,
                'خطا در پردازش! لطفا مجدد تلاش نمایید '
            )
            return redirect(url)



def count_followers(request,shop_id):
    return FolloweUnFollow.objects.filter(shop=get_object_or_404(Shop,id = shop_id)).count()



def list_followers(request,shop_id):
    return render(
        request,
        'follow/list_follwers.html',
        {
            'followers':FolloweUnFollow.objects.filter(
                shop__id = shop_id
            ),
            'len':count_followers(
                request,shop_id
            )
        }
    )