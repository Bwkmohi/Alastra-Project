from django.shortcuts import render,get_object_or_404,redirect
from .models import GroupCart
from django.contrib.auth.models import User
from django.contrib import messages
from cart.models import Cart
from django.utils import timezone
import openpyxl
from django.http import HttpResponse
from shop.models import Products
from accaunts.check_auth import check_user
from cart.views import get_cart_data



def create_group_cart(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')
    
    if request.method == 'POST':
        group=GroupCart.objects.create(
            group_name = request.POST.get('group_name'),
            admin = request.user
        )

        group.users.add(request.user)

        for cart in Cart.objects.filter(user = request.user):
            group.carts.add(cart)

        messages.success(
            request,
            'سبد گروهی با موفقیت ایجاد شد.'
        )
        return redirect('group_c:group_cart_view',group.pk)
    else:
        return render(
            request,
            'group_cart/create_group_cart.html'
        )



def add_users_to_group(request,group_id):
    user = check_user(request)
    if not user:
        return redirect('acc:login')
    
    group=get_object_or_404(GroupCart,id=group_id,admin=user)

    if request.method == 'POST':
        try:
            user=User.objects.get(id=request.POST.get('user_id'))
            group.users.add(user)

            for cart in Cart.objects.filter(user=user):
                group.carts.add(cart)
            messages.success(
                request,
                'کاربر با موفقیت افزوده شد!'
            )
            return redirect('group_c:group_cart_view',group_id)
        
        except User.DoesNotExist:
            messages.error(
                request,
                'error'
            )
            return redirect('group_c:group_cart_view',group_id)
    return HttpResponse('Error')    
 


def group_cart_view(request, group_id):
    group = get_object_or_404(GroupCart, id=group_id)
    user_carts = {}

    for cart in Cart.objects.filter(user__in=group.users.all()):
        if not cart in group.carts.all():
            group.carts.add(cart)

    for user in group.users.all():
        user_carts[user] = group.carts.filter(user=user)
 
    return render(
        request, 
        'group_cart/group_cart_view.html', 
        {
            'group': group,
            'user_carts': user_carts,
            'total_price': group.total_prices(),
        }
    )



def remove_user_from_group(request,user_id,group_id):
    user = check_user(request)

    if not user:
        return redirect('acc:pro')

    group=get_object_or_404(GroupCart,id=group_id,admin=user)
    remove_user = get_object_or_404(User,id=user_id)

    if user == remove_user:
        messages.error(
            request,
            'نیمتواندید خودتان را از گروه حذف کنید'
        )
        return redirect('group_c:group_cart_view',group.pk)

    if remove_user in group.users.all():
        for cart in Cart.objects.filter(user = remove_user):
            group.carts.remove(cart)
        group.users.remove(remove_user)
    else:
        messages.error(
            request,
            'چنین کاربری در گروه وجود ندارد'
        )
        return redirect('group_c:group_cart_view',group_id)
    
    messages.success(
        request,
        'کاربر با موفقیت از گروه حذف شد!'
    )
    return redirect('group_c:group_cart_view',group.pk)



def remove_product_from_cart(request,group_id,cart_id):
    user = check_user(request)

    if not user:
        return redirect('acc:pro')
    
    group=get_object_or_404(GroupCart,id=group_id,admin=user)

    cart=get_object_or_404(Cart,id = cart_id)
    cart.delete()

    messages.success(
        request,
        'محصول با موفقیت از سبد گروهی حذف شد'
    )
    return redirect('group_c:group_cart_view',group.pk)



def group_member_cart(request,group_id,user_id):
    user = check_user(request)

    if not user:
        return redirect('acc:pro')
    
    get_object_or_404(GroupCart,id = group_id,admin = user)
    get_object_or_404(User,id = user_id)

    return render(
        request,
        'cart/cart2.html',
        {
            'cart':Cart.objects.filter(user=request.user),        
            'sellproducts':Products.objects.filter(is_sellprice=True,have=True),
            'cart_data':get_cart_data(request),
        }
    )



def get_export_from_cart(request, group_id):
    group = get_object_or_404(GroupCart, id=group_id)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Cart Faktor {group.group_name}"

    ws.append([
        'نام گروه سبد خرید',
        'نام کاربر',
        'نام محصول',
        'تعداد',
        'قیمت واحد',
        'قیمت کل سبد خرید',
        'کد کوپن',
        'کوپن اعمال شده',
    ])

    carts = group.carts.all()

    for cart in carts:
        ws.append([
            group.group_name,
            cart.user.username,
            cart.product.name,
            cart.quantity,
            cart.product.sell_price if cart.product.sell_price else cart.product.price,
            cart.self_cart_total_price(),
            cart.use_coupon_code.code if cart.use_coupon_code else '',
            'بله' if cart.coupon_applyed else 'خیر',
        ])


    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f'{group.group_name}_{timezone.now().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb.save(response)
    return response