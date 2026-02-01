from django.shortcuts import render , redirect,get_object_or_404
from .models import Reservation,OrderModel
from django.contrib import messages
from cart.models import Cart
from accaunts.check_auth import check_user,check_user_authentication
from shop.mange_product_quantity import cost_product_quantity
from cart.views import cart_clear
from cart.views import get_cart_data
from shop.models import Products
from walet.views import (
    get_or_create_wallet,
    check_wallet_balance,
    payment
)
from .models import ProvinceCategory
from .models import Citys
from group_cart.models import GroupCart
from reservations.models import OrderModel,Reservation
import openpyxl
from django.http import HttpResponse
from django.utils import timezone
from facelogin.views import check_secure_and_enter_password
from notifications.user_notification import notification_in_reserv_with_group_cart
from notifications.shop_notification import notification_in_new_reservation
from cart.views import cart_price_updater
from sellers.models import ShopRate
import re
from costs_fee.views import cost_from_order



def pay_with_walet(request,order_id):
    user_authentication=check_user_authentication(request)
    order=get_object_or_404(OrderModel,id = order_id)
    user_wallet=get_or_create_wallet(request,user_authentication)
    cart_price_updater(request)
    

    if not user_authentication:
        messages.warning(
            request,
            'بدون اهراز هویت نمیتوانید با کیف پول پرداخت کنید'
        )
        return redirect('acc:authentication')
    

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    

    for item in Reservation.objects.filter(order = order,paid = False):
        seller_wallet=get_or_create_wallet(
            request,item.shop.seller.user_authentication
        )
        
        if check_wallet_balance(user_wallet,item.totalprice) == True:
            payment(
                request,
                item.totalprice,
                seller_wallet.pk
            )
            item.paid = True
            order.paid = True
            order.save()
            item.save()
            cost_product_quantity(order_id)
            cost_from_order(request,order.pk)
            messages.success(
                request,
                'پرداخت شما موفقیت امیز بود! '
            )
        else:
            messages.warning(
                request,
                 'پول کاقی برای پرداخت این سفارش ندارید! میتونید موجودی خود را افزایش دهید!'
            )
            return redirect('walet')
    return redirect('res:list_reservations')    


 

def reservation(request):
    user = check_user(request)
    cart_price_updater(request)


    if not user:
        messages.error(
            request,
            'نمیتوانید بدون ثبت نام سفارش ثبت کنید'
        )
        return redirect('acc:login')
    

    if get_cart_data(request) is None:
        messages.error(
            request,
            'با سبد خرید خالی نمیتوانید سفارش ثبت کنید . لطفاابتدا سبد خرید خود را کامل پر کیند'
        )
        return redirect('cart:cart')
    

    if request.method == 'POST':
        order = OrderModel.objects.create(
            name = request.POST.get('name') ,
            lastname = request.POST.get('lastname'),
            user = user ,
            email = user.email,
            phone = request.POST.get('phone'),
            address = request.POST.get('address'),
            province = get_object_or_404(ProvinceCategory,id = request.POST.get('province')),
            city = get_object_or_404(Citys,id =request.POST.get('city')),
            postaddress = request.POST.get('postaddress'),
            total_price = get_cart_data(request).cart_total_price(),
            payment_method = request.POST.get('payment_method'),
        )


        for item in Cart.objects.filter(user=user):
            if (
                item.product.active is False and
                item.product.have is False or
                item.product.qunat == 0 or
                item.quantity > item.product.qunat
            ):
                messages.info(
                    request, 
                    'تعداد سفارش بیشتر از موجودی انبار' if item.quantity > item.product.qunat else 'این محصول در انبار موجود نمیباشد '
                )
                return redirect('cart:cart')


            r = Reservation.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                totalprice=item.self_cart_total_price(),
                shop=item.product.shop,
                payment_method=order.payment_method
            )

            notification_in_new_reservation(r.pk)
            cart_clear(request)

            messages.success(
                request, 
                'سفارش شما با موفقیت ثبت شد'
            )

        if order.payment_method == 'ZARRINPAL':
            return redirect('zarinpal_request',order.pk)
        
        elif order.payment_method == 'WALLET':
            return redirect('res:pay_with_walet', order.pk)

    else:
        return render(
            request,
            'reservations/reservation.html',
            {
                'user': user,
                'province': ProvinceCategory.objects.all(),
                'cart': Cart.objects.filter(user=user),
                'city':Citys.objects.all()
            }
        )



#   سفارش با سبد خرید گروهی
def reservation_with_group_cart(request,group_id):
    group = get_object_or_404(GroupCart, id=group_id,admin=request.user)
    carts = group.carts.all()
    user = check_user(request)
    cart_price_updater(request)

    if not user:
        return redirect('acc:login')
    
    is_exist = 0

    group_cart = GroupCart.objects.filter(admin=user)
    for cart in group_cart:
        
        if cart.carts.exists():
            is_exist += 5

    if is_exist < 1:
        messages.error(
            request,
            'با سبد خالی نمیتوانید سفارش ثبت کنید!'
        )
        return redirect('group_c:group_cart_view',group_id)


    for cart in group_cart:cart = cart.carts.all()
    

    if request.method == 'POST':
        order = OrderModel.objects.create(
            name = request.POST.get('name') ,
            lastname = request.POST.get('lastname'),
            user = user ,
            email = user.email,
            phone = request.POST.get('phone'),
            address = request.POST.get('address'),
            payment_method = request.POST.get('payment_method'),

            province = get_object_or_404(ProvinceCategory,id = request.POST.get('province')),
            city = get_object_or_404(Citys,id =request.POST.get('city')),
            postaddress = request.POST.get('postaddress'),
            total_price = get_cart_data(request).cart_total_price(),
        )
        print('I AM DOED IT')

 
        for cart in carts:
            try:
                reservation, created = Reservation.objects.get_or_create(
                    order=order,
                    product=cart.product,                    
                    shop = cart.product.shop,
                    payment_method =order.payment_method,
                    defaults={
                        'quantity': cart.quantity,
                        'totalprice': cart.self_cart_total_price(),
                    }
                ) 
                notification_in_new_reservation(reservation.pk)
                cart.delete()
                print(f'Creating reservation for product {cart.product} with price {cart.product.price}')


            except Exception as e:
                print(f'Error creating reservation for product {cart.product}: {e}')


            if not created:
                reservation.quantity += int(cart.quantity)
                reservation.totalprice = int(cart.self_cart_total_price())
                reservation.save()

        notification_in_reserv_with_group_cart(group_id)
        
        if order.payment_method == 'WALLET':
            return redirect('res:pay_with_walet', order.pk)
        
        elif order.payment_method == 'ZARRINPAL':
            return redirect('zarinpal_request',order.pk)
        
    else:
        return render(
            request,
            'reservations/reservation.html',
            {
                'user': user,
                'province': ProvinceCategory.objects.all(),
                'cart': cart,
                'city':Citys.objects.all(),
                'is_group_cart':True
            }
        )
        


#  پرداخت مجدد. در صورت پرداخت قبلی نا موفق
def pay_again(request,order_id,pay_with):
    order = get_object_or_404(OrderModel,id = order_id,paid = False)

    Reservation.objects.filter(
        order__id = order.pk
    )

    if pay_with == 'zarinpal':
        return redirect('zarinpal_request',order.pk)
    
    elif pay_with == 'wallet':
        return redirect('res:pay_with_walet', order.pk)


# تکرار خرید
def repeat_purchase(request, order_id,pay_type):
    original_order = get_object_or_404(OrderModel, id=order_id)
    cart_price_updater(request)

    original_order.pk = None
    original_order.tracking_code = None  
    original_order.paid = False          
    original_order.created_at = None 
    original_order.save()
    new_order = original_order
    
    if pay_type == 'zarinpal':
        new_order.payment_method = 'ZARRINPAL'
        new_order.save()
    else:
        new_order.payment_method = 'WALLET'
        new_order.save()

    reservations = Reservation.objects.filter(order_id=order_id)

    for i in reservations:
        notification_in_new_reservation(i.pk)
            
    for res in reservations:

        res.pk = None
        res.order = new_order
        res.canceled = False
        res.paid = False
        res.tracking_code = None
        res.delivered = False
        res.sent_to_post = False
        res.post_delivery = False
        res.preparation = False
        res.save()
        



    if pay_type == 'zarinpal':
        messages.success(
            request,
            'سفارش با موفقیت ثبت شد!'
        )
        return redirect('zarinpal_request',new_order.pk)
    
    else:
        messages.success(
            request,
            'سفارش با موفقیت ثبت شد!'
        )
        return redirect('res:pay_with_walet', new_order.pk)



def make_true_order_model(order_id):
    order = get_object_or_404(OrderModel,id=order_id)
    Reservation.objects.filter(order=order).update(paid=True)


from copon2.models import SaveCoupon

def user_addreses(request):
    user = check_user(request)

    if not user:
        messages(
            request,
            'ابتدا ثبت نام کنید'
        )
        return redirect('acc:sign')
    

    if request.method == 'POST':
        order_id = request.POST.get('id')


        try:
            order = OrderModel.objects.get(id=order_id)
            con = {'order':order,'province':ProvinceCategory.objects.all(),'city':Citys.objects.all()}
            messages.success(
                request,
                'ادرس انتاب شد! لطفا در ادامه اطلاعات را تایید کنید'
            )
            return render(request, 'reservations/reservation.html', con)


        except OrderModel.DoesNotExist:             
            messages.error(
                request,
                'اطلاعات انتخاب شده وجود ندارد! '
            )
            return redirect('res:res')


    else:
        order = OrderModel.objects.filter(user=user)
        if order.exists():
            con = {
                'adresses': order,
                'saved_coupons':SaveCoupon.objects.filter(user=user)
            }
            return render(request, 'reservations/user_addreses.html', con)
        return render(request, 'reservations/reservation.html',{'province':ProvinceCategory.objects.all(),'city':Citys.objects.all()})

def list_product_ids(request):
    list_product_ids = []
    for i in Reservation.objects.filter(order__user = request.user):
        if i.product.pk not in list_product_ids:
            list_product_ids.append(i.product.pk)
    return list_product_ids


 
def list_reservations(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    products = Products.objects.filter(id__in = list_product_ids(request))
    return render(
        request,
        'reservations/list_reservations.html',
        {
            'reservations':Reservation.objects.filter(order__user = request.user).order_by('-order__created_at'),
            'products':products if products else '',
        }
    )
    


 

def order_detail(request,id):
    user = check_user(request)
    open_rate_modal_premess = []
    
    if not user:
        return redirect('acc:login')
    

    reservation=Reservation.objects.filter(order__id = id,order__user = user)


    for i in reservation:
        if i.delivered == True:
            if not ShopRate.objects.filter(reserv=i).exists():
                open = True
            else:
                open = False
        else:open=False


        open_rate_modal_premess.append(
            {
                'open':open,
                'name_shop':i.shop.name_shop,
                'id':i.pk
            }
        )


    return render(
        request,
        'reservations/order_detail.html',
        {
            'order':get_object_or_404(OrderModel,id = id),
            'reservs':reservation,
            'count':reservation.count(),
            'open_rate_modal_premess':open_rate_modal_premess
            
        }
    )



def cancel_order(request,reserv_id):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    
    try:
        reserv=Reservation.objects.get(
            id = reserv_id,
            order__user = user,
            order__paid = True
        )
            

        if reserv.canceled == True:
            messages.warning(
                request,
                'این سفارش قبلا لغو شده است'
            )
            return redirect('res:list_reservations')


        if reserv.sent_to_post == False and reserv.post_delivery == False and reserv.delivered == False:
            reserv.canceled = True
            reserv.save()
            messages.success(
                request,
                'سفارش با موفقیت لغو شد!'
            )
            return redirect('res:list_reservations')


        else:
            messages.warning(
                request,
                'این محصول توسط فروشنده ارسال شده امکان لغو ان نیست '
            )
            return redirect('res:list_reservations')


    except Reservation.DoesNotExist:
        messages.warning(
            request,
            'چنین سفارشی وجود ندارد'
        )
        return redirect('res:list_reservations')



def slugify_filename(s):
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'[-\s]+', '_', s)
    return s



def order_export(request, order_id):
    user = check_user(request)

    if not user:
        return redirect('acc:login')


    try:
        order = OrderModel.objects.get(id=order_id, user=user)
    except OrderModel.DoesNotExist:
        return HttpResponse("سفارش یافت نشد یا دسترسی ندارید.", status=404)


    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "سفارشات"

    ws.append([
        'شماره سفارش',
        'نام محصول',
        'ای دی کاربر',
        'ای دی محصول',
        'تعداد',
        'نام گیرنده',
        'نام خانوادگی',
        'شماره تلفن گیرنده',
        'آدرس',
        'استان',
        'شهر',
        'کد پستی',
        'کد پیگیری',
        'نام فروشگاه',
        'دریافت شده',
        'کنسل شده',
        'قیمت کل',
        'تاریخ سفارش'
    ])


    for r in Reservation.objects.filter(order=order):
        ws.append([
            r.pk,
            r.product.name,
            r.order.user.pk,
            r.product.pk,
            r.quantity,
            r.order.name,
            r.order.lastname,
            r.order.phone,
            r.order.address,
            r.order.province.name,
            r.order.city.name,
            r.order.postaddress,
            r.order.tracking_code or '',
            r.shop.name_shop,
            'بله' if r.delivered == True else 'خیر',
            'شده' if r.canceled == True else 'نشده',
            r.order.total_price,
            r.order.created_at.strftime('%Y-%m-%d'),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    safe_first_name = slugify_filename(user.first_name)
    filename = f'orders_{safe_first_name}_{timezone.now().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response