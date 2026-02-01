from django.shortcuts import render
from shop.models import Products,ProductKeyValues
from django.db.models import Q
from itertools import chain
from django.db.models import Count, Avg
from smartgtp.viewed import ViewedProducts
from shop.models import Products
from reservations.models import Reservation
from accaunts.check_auth import check_user
from follow.models import FolloweUnFollow
from watchlist.models import WatchList
from cart.models import Cart 
from shop.views import context_send_html






 
def get_smart_suggestions_from_reserv_history(request):
    user = check_user(request)
    recent_products = Products.objects.all().order_by('-created')


    product_ids = list(
        Reservation.objects.filter(order__user=user)
        .values_list('product__pk', flat=True)
        .distinct()
    )


    if not user:    
        return render(
            request, 
            'shop/products.html',
            context_send_html(request, recent_products)
        )


    if not product_ids:
        recent_products = Products.objects.all().order_by('-created')
        return render(
            request,
            'smartgtp/products.html',
            context_send_html(request, recent_products)
        )


    filters = Q()
    pkvs = ProductKeyValues.objects.filter(product__id__in=product_ids).select_related('product')
    for pkv in pkvs:
        filters |= (
            Q(key=pkv.key) |
            Q(product__brand=pkv.product.brand) |
            Q(product__color=pkv.product.color) |
            Q(product__category=pkv.product.category)
        )


    filtered_products = ProductKeyValues.objects.filter(filters).exclude(product__id__in=product_ids).distinct()
    suggested_product_ids = filtered_products.values_list('product__pk', flat=True).distinct()
    products = Products.objects.filter(id__in=suggested_product_ids)

    return render(
        request, 
        'shop/products.html', 
        context_send_html(request,products)
    )

 

def get_exemple_products(request, list_product_ids):

    if not list_product_ids:
        return Products.objects.all().order_by('-created')


    filters = Q()
    for p in ProductKeyValues.objects.filter(product__id__in=list_product_ids):
        filters |= (
            Q(key=p.key) |
            Q(product__brand=p.product.brand) |
            Q(product__color=p.product.color) |
            Q(product__category=p.product.category)
        )

    list_ids = set()
    filtered_products = ProductKeyValues.objects.filter(filters).exclude(product__id__in=list_product_ids).distinct()

    for item in filtered_products:
        list_ids.add(item.product.pk)

    return Products.objects.filter(id__in=list_ids)

  
 
def best_selling_view(request):
    product_ids = []

    
    best_selling = Reservation.objects.annotate(
        total_sales=Count('product')  # 'product' همان related_name در Reservation
    ).order_by('-total_sales')


    for i in best_selling:
        product_ids.append(i.product.pk)
    
        
    return render(
        request,
        'shop/products.html',
        context_send_html(request,Products.objects.filter(id__in=product_ids))
    )
 
  

def popular_products_view(request):

    popular = Products.objects.annotate(
        avg_rating=Avg('product__rating')  # 'product' همان related_name در Comments
    ).order_by('-avg_rating')

    return render(
        request,
        'shop/products.html', 
        context_send_html(request,popular)
    )
 


def last_viewed_products(request):
    history = ViewedProducts(request).get()   

    return render(
        request,
        'shop/products.html',
        context_send_html(request,Products.objects.filter(
            id__in=history
            )
        )
    )

 

def special_products(request):
    product_ids = []

    for i in Reservation.objects.annotate(total_sales=Count('product')  # 'products' همان related_name در Reservation
        ).order_by('-total_sales'):
        product_ids.append(i.product.pk)


    best_selling=Products.objects.filter(id__in=product_ids)
    discounted = Products.objects.filter(is_sellprice=True)
    special = Products.objects.filter(spessial=True)


    seen = set()
    unique_products = []
    for product in list(chain(best_selling, discounted, special)):
        if product.id not in seen:
            unique_products.append(product.pk)
            seen.add(product.id)


    return render(
        request,
        'shop/products.html',
        context_send_html(request, Products.objects.filter(id__in=unique_products))
    )

 

def exemple_my_watchlist_products(request):

    user = check_user(request)
    if not user:
        return render(
            request,
            'shop/products.html',
            context_send_html(
                request,
                Products.objects.all().order_by('-created')

            )
        )
        
    list_ids = WatchList.objects.filter(user=user).values_list('product__pk', flat=True)


    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            get_exemple_products(request,list_ids)
        )
    )
 


def exemple_cart_products(request):

    user = check_user(request)
    if not user:
        return render(
            request,
            'shop/products.html',
            context_send_html(
                request,
                Products.objects.all().order_by('')
            )
        )
     
    list_ids = Cart.objects.filter(user=user).values_list('product__pk', flat=True)

    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            get_exemple_products(
                request,
                list_ids
            )
        )
    )

 
 

def sell_price_products(request):
    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            get_exemple_products(
                request,
                Products.objects.filter(
                    is_sellprice = True
            )
            )
        )
    )
 


def viewedest(request):
    products = Products.objects.all()
    list_views = [product.views for product in products]
    count = products.count()

    if count == 0 or sum(list_views) == 0:
        return render(
            request,
            'shop/products.html',
            context_send_html(
                request,
                products
            )
        )

    avg_views = sum(list_views) / count

    product_model = Products.objects.filter(views__lte=avg_views)

    list_ids = product_model.values_list('pk', flat=True)

    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            get_exemple_products(request, list_ids)
        )
    )

 


def my_following_shop_products(request):
    user = check_user(request)
    if not user:
        return None

    list_products = []

    # جمع‌آوری محصولات همه فروشگاه‌هایی که کاربر دنبال کرده
    for follow in FolloweUnFollow.objects.filter(user=user):
        products = Products.objects.filter(shop=follow.shop)
        list_products.extend(products.values_list('id', flat=True))  # لیست آیدی محصولات را اضافه می‌کنیم

    products_qs = Products.objects.filter(id__in=list_products).distinct()

    return render(
        request,
        'shop/products.html',
        context_send_html(request, products_qs)
    )
