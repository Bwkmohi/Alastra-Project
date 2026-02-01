from django.shortcuts import render ,redirect,get_object_or_404
from shop.models import Products
from django.contrib import messages
from smartgtp.viewed import ViewedProducts
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from accaunts.check_auth import check_user
from .models import Cart
from django.http import JsonResponse, Http404
from copon2.models import SaveCoupon



def cart_price_updater(request):
    for item in Cart.objects.filter(user = request.user):
        if not item.use_coupon_code and item.coupon_applyed == False:
            item.total_price = item.self_cart_total_price()
            item.save()    



def cart(request):
    user = check_user(request)
    if not user:
        return redirect('acc:login')
        
    recommended_products = None
    history_ids = ViewedProducts(request).get()

    if history_ids:
        history_ids = [
            int(x) for x in history_ids if str(x).isdigit()
        ]

        exclude_id = history_ids[
            0
        ] if history_ids else None

        if exclude_id:
            recommended_products = Products.objects.filter(id__in=history_ids)
        else:
            recommended_products = []

        recommended_products = Products.objects.filter(id__in=history_ids)
 
    return render(
        request,
        'cart/cart2.html',
        {
            'cart':Cart.objects.filter(user=request.user),        
            'sellproducts':Products.objects.filter(is_sellprice=True,have=True),
            'recommended_products':recommended_products,
            'cart_data':get_cart_data(request),
            'saved_coupons':SaveCoupon.objects.filter(user = request.user)
        }
    )



def cart_add(request):
    user = check_user(request)
    cart_price_updater(request)

    if not user:
        return redirect('acc:login')

    if request.method == 'POST':
        product = get_object_or_404(
            Products, id=request.POST.get('id')
        )
        qty = request.POST.get('qty')
        url = request.POST.get('url')

        try:
            cart = Cart.objects.get(user=user, product=product)
            cart.quantity += 1
            cart.save()

            messages.success(
                request,
                'تعداد محصول سبد بروز شد '
            )
            return redirect(url if url else 'cart:cart')

        except Cart.DoesNotExist:
            Cart.objects.create(user=user, product=product, quantity=qty)
            messages.success(
                request,
                'محصول با موفقیت به سبد خرید اضافه شد .'
            )
            return redirect(url if url else 'cart:cart')



@csrf_exempt
def add_to_cart(request):

    if request.method == "POST":
        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])
        
        for id in product_ids:
            product = get_object_or_404(Products,id = id)

            if Cart.objects.filter(product = product).exists():pass
            else:Cart.objects.create(user = request.user,product = product)

        return JsonResponse({
            'status': 'success', 'action': 'cart', 'ids': product_ids,'success':True
        })
    return JsonResponse({
        'status': 'error','success':False
    })

    

@require_POST
def cart_edit_quantity1(request):
    try:
        c = Cart.objects.get(id=request.POST.get('id'))
        c.quantity += 1
        c.save()
    except Cart.DoesNotExist:pass

    cart_price_updater(request)

    return JsonResponse(
        {
            'success': True,
            'qty_add': c.quantity
        }
    )



@require_POST
def cart_edit_quantity2(request):
    cart_price_updater(request)

    try:
        cart=Cart.objects.get(id = request.POST.get('id'))

        if cart.quantity == 1:cart.quantity += 1
        else:cart.quantity -= 1 
        cart.save()

    except Cart.DoesNotExist:
        pass

    return JsonResponse(
        {
            'success': True,
            'qty_mines':cart.quantity
        }
    )



def cart_qty(request, id):
    try:
        return JsonResponse({
            'cart_qty': Cart.objects.get(pk=id).cart_quantity()
        })
    except (Products.DoesNotExist):
        raise Http404("محصول پیدا نشد")



def cart_remove(request,id):  
    try: 
        Cart.objects.get(id=id).delete()
        messages.success(
            request,
            'محصول شما با موفقیت از سبد خرید حذف شد'
        )
        return redirect('cart:cart')
    
    except Cart.DoesNotExist:
        messages.warning(
            request,
            'خطا در حذف سبد خرید و لطفا مجدد تلاش کنید'
        )
        return redirect('cart:cart')
    


def get_cart_data(request):
    for item in Cart.objects.filter(user = request.user)[:1]:
        try:
            return Cart.objects.get(id = item.pk)
        except Cart.DoesNotExist:return None
    return None



def cart_clear(request):
    for item in Cart.objects.filter(user = request.user):
        item.delete() 