from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from shop.models import Products
from copon2.models import Coupon,SaveCoupon
from follow.check_follow import checkFollow
from accaunts.check_auth import check_user
from cart.views import cart_price_updater


def coupon_apply(request):
    from cart import models

    user = check_user(request)
    if not user:
        return redirect('acc:login')

    if request.method == "POST":
        cart_price_updater(request)
        url = request.POST.get('url')
 
        coupon_applied = False
        try:
            code_value=request.POST.get('code')
            if code_value:
                coupon = Coupon.objects.get(
                    code__iexact=code_value,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now(),
                    active=True,
                )
                print(coupon)
            else:return redirect(url if url else 'cart:cart')
        except Coupon.DoesNotExist:
            messages.error(
                request,
                "کوپن نامعتبر است."
            )
            return redirect(url if url else 'cart:cart')

        for cart_items in models.Cart.objects.filter(user=user):
            if cart_items.coupon_applyed == True:
                messages.warning(
                    request,
                    'کوپن برایتان فعال شده است!'
                )
                return redirect(url if url else 'cart:cart')

            try:
                product = Products.objects.get(id=cart_items.product.pk)
            except Products.DoesNotExist:
                continue

            if coupon.usage_limit:
                if coupon.usage_limit == coupon.used_count:
                    messages.warning(
                        request,
                        'محدودیت استفاده فعال شده است ! متاسفانه نمیتوانید استفاده کنید'
                    )
                    coupon.active = False
                    coupon.save()
                    return redirect(url)

            if coupon.category is None:
                # اگر کوپن تگ ندارد، کوپن روی همه محصولا اعمال می‌شود
                coupon_applied = True
            else:
                if product.main_cattegory.filter(id=coupon.category.pk).exists():
                    coupon_applied = True

            if coupon_applied:
                if coupon.for_followers == True:
                    if for_follower_coupon(request, coupon, user, cart_items.product) == True:
                        if str(coupon.shop.pk) == str(cart_items.product.shop.pk):
                            Apply(
                                request,
                                cart_items=cart_items,
                                coupon=coupon
                            )
                            messages.success(
                                request,
                                'کوپن با موفقیت اعمال شد '
                            )
                        else:
                            messages.warning(
                                request,
                                f'{cart_items.product.name}  شامل فروشگاه دیگر میباشد . ما نمیتونیم تخفیف اعمال کنیم'
                            )
                    else:
                        messages.warning(
                            request,
                            'ایم کوپن مخصوص کاربرانی که که فروشگاه را فالو میکنند است .'
                        )
                else:
                    Apply(
                        request,
                        cart_items,
                        coupon
                    )
                    messages.success(
                        request,
                        'کوپن با موفقیت اعمال شد !'
                    )
            else:
                messages.error(
                    request,
                    "کوپن برای محصولات سبد شما معتبر نیست."
                )
                return redirect(url if url else 'cart:cart')

            messages.success(
                request,
                'کوپن اعمال شد . حالشو ببر'
            )
        return redirect(url if url else 'cart:cart')



def Apply(request,cart_items,coupon): 

    coupon.used_count += 1
    coupon.save()
    
    # if coupon.is_percent == True:
    #     result = (Decimal(coupon.value) / Decimal(100)) * cart_items.self_cart_total_price()

    # elif coupon.is_percent == False:
    #     result = cart_items.self_cart_total_price() - coupon.value

    # res = cart_items.total_price - max(result, Decimal(0))
    # cart_items.total_price = res
    cart_items.coupon_applyed = True
    cart_items.use_coupon_code = coupon
    try:
        SaveCoupon.objects.get(coupon=cart_items.use_coupon_code,user=request.user).delete()
    except SaveCoupon.DoesNotExist:
        ''
    cart_items.save()



def for_follower_coupon(request,coupon,user,product):
    return checkFollow(request,product.shop.pk,user_id=user.id)



def saved_coupons(request):
    return render(
        request,
        'coupon2/saved_coupons.html',
        {
            'coupons':SaveCoupon.objects.filter(
                user = check_user(request)
            )
        }
    )

 

def remove_coupon_from_saves(request,id):
    
    coupon = get_object_or_404(SaveCoupon,user = check_user(request),id = id)
    coupon.delete()
    messages.success(
        request,
        'کوپن با موفقیت حذف شد!'
    )
    return redirect('saved_coupons')

def save_coupon(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            coupon=Coupon.objects.get(
                code__iexact=code
            )

            if SaveCoupon.objects.filter(user = user,coupon=coupon).count() > 5:
                messages.info(
                    request,
                    'شما نمیتوانید بیشتر از 5 کوپن ذخیره کنید!'
                )
                return redirect('saved_coupons')
            
            if SaveCoupon.objects.filter(coupon=coupon,user=user).exists():
                return redirect('saved_coupons')

            SaveCoupon.objects.create(
                user = user,
                coupon = coupon
            )
            messages.success(
                request,
                'کوپن با موفقیت افزوده شد!'
            )
        except Coupon.DoesNotExist:
            messages.warning(
                request,
                'چنین کوپنی یافت نشد!'
            )
            return redirect('saved_coupons')

        return redirect('saved_coupons')
    return redirect('saved_coupons')
        