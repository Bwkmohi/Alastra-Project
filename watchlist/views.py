from django.shortcuts import render,redirect,get_object_or_404
from .models import WatchList
from accaunts.check_auth import check_user
from shop.models import Products
from django.contrib import messages
from django.shortcuts import redirect
from shop.models import Products
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.core.mail import send_mail
from config import settings
from django.http import HttpResponse,Http404
from cart.models import Cart



@csrf_exempt
def add_to_watchlist_by_list(request):
    if request.method == "POST":

        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])

        for id in product_ids:
            if not WatchList.objects.filter(product__id=id,user = request.user).exists():    

                WatchList.objects.create(
                    product = get_object_or_404(Products, id = id),
                    user = request.user,
                )

            else:pass

        return JsonResponse({
            'status': 'success', 'action': 'cart', 'ids': product_ids
        })
    return JsonResponse({
        'status': 'error'
    })



@csrf_exempt
def remove_from_watchlist_by_list(request):
    if request.method == "POST":

        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])

        WatchList.objects.filter(user = request.user,product__id__in = product_ids).delete()

        return JsonResponse({
            'status': 'success',
        })
    return JsonResponse({
        'status': 'error'
    })
 


def watch_list(request):
    user = check_user(request)
    watch_list = WatchList.objects.filter(user = user)

    if not user:
        return redirect('acc:login')
        
    return render(
        request,
        'watchlist/watch_list.html',
        {
            'products':watch_list,
            'len':watch_list.count(),
        }
    )



def watchlist_remove(request,id):
    get_object_or_404(WatchList,id = id).delete()

    messages.success(
        request,
        'محصول از واچ لیست حذف شد!'
    )
    return redirect('watchlist:watch_list')



def watchlist_add(request):
    user = check_user(request)
    
    if not user:
        return redirect('acc:login')


    if request.method == 'POST':

        product_id = request.POST.get('id')
        url = request.POST.get('url')
        
        product = get_object_or_404(
            Products, id=product_id
        )

        for item in WatchList.objects.filter(user=user):

            if item.product.pk == int(product_id) or str(product_id) in str(item.product.pk):
                messages.warning(
                    request,
                    'محصول از قبل در واچ لیست شما وجود دارد .نیازی به افزودن دوباره نیست'
                )
                return redirect(url if url else 'watchlist:watch_list')

        WatchList.objects.create(
            user=user,
            product=product,
            send_notification=True,
        )
        messages.success(
            request,
            'محصول با موفقیت به .اچ لیست اضافه شد!'
        )

        return redirect(url if url else 'watchlist:watch_list')

    else:
        return Http404('404')



def add_or_edit_alert(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        alert_price = request.POST.get('alert_price')
        direction = request.POST.get('direction')
        alert_in_change_price = request.POST.get('alert_in_change_price')
        send_notification = request.POST.get('send_notification')
        print(id,  id,id)
        watch_list = get_object_or_404(WatchList,id = id)

        if alert_price:
            watch_list.alert_price = alert_price
            watch_list.save()

        if direction:
            watch_list.direction = direction
            watch_list.save()

        if alert_in_change_price:
            watch_list.alert_in_change_price = bool(alert_in_change_price)
            watch_list.save()

        if send_notification:
            watch_list.send_notification = bool(send_notification)
            watch_list.save()

        return redirect('watchlist:watch_list')



def add_cart_from_wactchlist(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    
    for watchlist in WatchList.objects.filter(user = user):
        if not Cart.objects.filter(user = user,product = watchlist.product).exists():
            Cart.objects.create(
                product = watchlist.product,
                user = user,
            )

    messages.success(
        request,
        'محصولات واچ لیست به سبد خریدافزوده شدند!'
    )
    return redirect('cart:cart')
    


def clear_watchlist(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    
    WatchList.objects.filter(user = user).delete()
    messages.success(
        request,'واچ لیست شما با موفقیت خالی شد!'
    )
    return redirect('products_list')


#
def check_price_and_notify(request):
    watchlists = WatchList.objects.filter(send_notification=True, alert_price__isnull=False, is_triggered=False)
    sent_count = 0


    for watch in watchlists:
        current_price = watch.product.price_()  
        
        if watch.direction == 'above' and current_price >= watch.alert_price:

            send_mail(
                subject=f'هشدار قیمت برای {watch.product.name}',
                message=f'قیمت محصول {watch.product.name} به {current_price} رسیده است که بیشتر از قیمت هشدار شما ({watch.alert_price}) می باشد.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[watch.user.email],
                fail_silently=False,
            )
            
            watch.is_triggered = True
            watch.save()
            sent_count += 1
        

        elif watch.direction == 'below' and current_price <= watch.alert_price:

            send_mail(
                subject=f'هشدار قیمت برای {watch.product.name}',
                message=f'قیمت محصول {watch.product.name} به {current_price} رسیده است که کمتر از قیمت هشدار شما ({watch.alert_price}) می باشد.',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[watch.user.email],
                fail_silently=False,
            )

            watch.is_triggered = True
            watch.save()
            sent_count += 1

    return HttpResponse(f"تعداد هشدارهای ارسال شده: {sent_count}")