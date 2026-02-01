from django.shortcuts import render,get_object_or_404 ,redirect
from shop.models import Products
from django.contrib import messages
from sellers.check import get_shop
from django.db.models import Avg, Count, Sum
from watchlist.models import WatchList
from cart.models import Cart
from facelogin.views import check_secure_and_enter_password
from collaborator.views import check_collab_and_jobs
from accaunts.check_auth import check_user
from collaborator.views import create_activity,check_collabrator
from reservations.models import Reservation
from smartgtp.views import get_exemple_products
from shop.models import Comments
from django.db.models import Count, Avg           
from shop.models import MainCategory,ColorCategory,BrandCategory,ProductDetaKeys,ProductKeyValues,SuperCategory
from copon2.models import Coupon
from watchlist.views import check_price_and_notify
from notifications.user_notification import notification_in_add_product,notification_in_edit_product_price_or_sell_price
from django.shortcuts import render, redirect, get_object_or_404
from sellers.models import Shop
import bleach


def product_analysis(request,product_id,shop_id):

    if check_collab_and_jobs(request,'can_see_products',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    product = get_object_or_404(Products,id=product_id,shop__id = shop_id)
    cart_count = Cart.objects.filter(product=product).count()
    watchlist_count = WatchList.objects.filter(product=product).count()

    total_purchased = Reservation.objects.filter(
        product=product, paid=True
    ).aggregate(total_qty=Sum('quantity'))['total_qty'] or 0

    views_count = product.views
    likes_count = product.like.count()
    similar_count = get_exemple_products(request,list_product_ids=[product.pk]).count()

    product_profit = Reservation.objects.filter(
        shop=shop_id,
        order__paid=True,
        product__id=product.pk
    ).aggregate(total_profit=Sum('totalprice'))['total_profit'] or 0

    top_province = Reservation.objects.filter(
        product=product, paid=True
    ).values('order__province__name').annotate(
        total=Count('id')
    ).order_by('-total').first()
    top_province_name = top_province['order__province__name'] if top_province else 'نامشخص'
    avg_rating = Comments.objects.filter(product=product).aggregate(
        avg=Avg('rating')
    )['avg'] or 0


    return render(
        request,
        'shop_manage_products/product_analysis.html',
        {
            'cart_count': cart_count,
            'shop_id':shop_id,
            'watchlist_count': watchlist_count,
            'total_purchased': total_purchased,
            'views_count': views_count,
            'likes_count': likes_count,
            'similar_count': similar_count,
            'total_profit': product_profit,
            'top_province': top_province_name,
            'avg_rating': round(avg_rating, 2),
        }
    )



def products_list(request,shop_id): 

    shop = get_object_or_404(Shop,id = shop_id,reported=False)
    list_products = []
    products = Products.objects.filter(shop = shop).order_by('-created')


    if check_user(request):

        if check_secure_and_enter_password(request,'self_function_checking') == True:
            url = f'{request.path}'.replace('/','%')
            return redirect('enter_password',redirect_url=f'{url}')
        
        if check_collab_and_jobs(request,'can_see_products',shop_id)==False:
            messages.warning(
                request,
                'شما به این بخش دسترسی ندارید!'
            )
            return redirect('acc:pro')
        

        for i in products:
            list_products.append(
                {
                    'name':i.name,
                    'price_':i.price_(),
                    'image':i.image,
                    'views':i.views,
                    'qunat':i.qunat,
                    'category':i.category,
                    'rate':i.total_rates(),
                    'active':i.active,
                    'comments_count':i.comments_count(),
                    'slug':i.slug,
                    'total_sale':i.total_sale(),
                    'have':i.have,
                    'id':i.id
                }
            )


        if products:
            return render(
                request,
                'shop_manage_products/products_list.html',
                {
                    'products':list_products,
                    'len':products.count()      ,
                    'super_category':SuperCategory.objects.all()
                }
            )
        
        else:return render(request,'shop_manage_products/products_list.html')
    else:return redirect('index')



def products_data(request,shop_id):
    if not check_collab_and_jobs(request, 'can_see_products', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    best_selling_products = (Reservation.objects.filter(shop=get_shop(request, shop_id), paid=True).values('product').annotate(sale_count=Count('product')).order_by('-sale_count')[:10])  
    

    return render(
        request,
        'shop_manage_products/products_data.html',
        { 
            'best_sales_products':Products.objects.filter(
                id__in=[int(i.get('product')) for i in best_selling_products]).order_by('-created')[
                    :10
                ],
        }
    )



def product_delete(request, id, shop_id):
    shop = get_shop(request, shop_id)
    if not shop:return redirect('acc:pro')
    product = get_object_or_404(Products, id=id, shop=shop)

    if not check_collab_and_jobs(request, 'product_delete', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)

    
    if check_collabrator(request, shop_id):
        create_activity(request, 'حذف محصول', product.pk, 'REMOVE', shop_id)

    product.delete()
    messages.success(
        request,
        'محصول با موفقیت حدف شد!'
    )
    return redirect('pro:products_list',shop_id)



def add_product(request, shop_id):

    if not check_collab_and_jobs(request, 'product_add', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    shop = get_shop(request, shop_id)
    if not shop:return redirect('')



    if request.method == 'POST':

        category_id = request.POST.get('category')
        color_id = request.POST.get('color')
        brand_id = request.POST.get('brand')
        is_sellprice = request.POST.get('is_sellprice')
        spessial = request.POST.get('spessial')
        active = request.POST.get('active')
        have = request.POST.get('have')
        sell_price = request.POST.get('sell_price')

        product = Products.objects.create(
            name=request.POST.get('name'),
            image=request.FILES.get('image'),
            price=int(request.POST.get('price')),
            description=bleach.clean(request.POST.get('description')),
            shop=shop,
            active=False,
            have=False,
        )

        product.description_seo = request.POST.get('description_seo')

        if category_id:
            product.category=get_object_or_404(SuperCategory, id=category_id)

        if color_id:
            product.color = get_object_or_404(ColorCategory, id = color_id)
        
        if brand_id:
            product.brand = get_object_or_404(BrandCategory, id = brand_id)

        product.main_cattegory.set(request.POST.getlist('main_category'))

        if not product.slug:
            product.slug = request.POST.get('slug')

        product.qunat = request.POST.get('qunat')

        if sell_price:
            product.sell_price = sell_price  


        product.is_sellprice = True if is_sellprice == 'on' or is_sellprice == 'True' else False
        product.active = True if active == 'on' or active == 'True' else False
        product.spessial = True if spessial == 'on' or spessial == 'True' else False
        product.have = True if have == 'on' or have == 'True' else False
        


        
        product.save()


        spec_keys = request.POST.getlist('spec_keys[]')
        spec_values = request.POST.getlist('spec_values[]')
        

        for key_id, value in zip(spec_keys, spec_values):
                if key_id and value:  
                    try:
                        key_obj = ProductDetaKeys.objects.get(id=key_id)
                        ProductKeyValues.objects.create(
                            product=product,
                            key=key_obj,
                            value=value
                        )
                    except ProductDetaKeys.DoesNotExist:
                        continue 
 
        check_price_and_notify(request)


        
        notification_in_add_product(product.pk,shop_id)


        if check_collabrator(request, shop_id):
            create_activity(request, 'افزودن محصول جدید مرحله 1', product.pk, 'ADD', shop_id)

        messages.success(
            request, 'محصول شما با موفقیت ایجاد شد!'
        )
        return redirect('pro:products_list',shop_id)



    else:
        return render(
            request, 
            'shop_manage_products/product_add.html', 
            {
                'super_categories': SuperCategory.objects.all(),
                'main_categories': MainCategory.objects.all(),
                'colors': ColorCategory.objects.all(),
                'brands': BrandCategory.objects.all(),
                'spec_keys': ProductDetaKeys.objects.all(),
                'shop_id':shop_id,
            }
        )

 

def edit_product(request, shop_id,product_id):

    product = get_object_or_404(Products,id=product_id)
    shop = get_shop(request, shop_id)
    if not shop:return redirect('')


    if not check_collab_and_jobs(request, 'product_add', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    if request.method == 'POST':

        category_id = request.POST.get('category')
        color_id = request.POST.get('color')
        brand_id = request.POST.get('brand')    
        product.name=request.POST.get('name')
        is_sellprice = request.POST.get('is_sellprice')
        spessial = request.POST.get('spessial')
        active = request.POST.get('active')
        have = request.POST.get('have')
        main_category = request.POST.getlist('main_category')
        product.description_seo = request.POST.get('description_seo')

        image = request.FILES.get('image')
        if image:
            product.image=image

        product.price=int(request.POST.get('price'))
        product.description=bleach.clean(request.POST.get('description'))
        product.active=False
        product.have=False
        
        if category_id:
            product.category=get_object_or_404(SuperCategory, id=category_id)

        if color_id:
            product.color = get_object_or_404(ColorCategory, id = color_id)
        
        if brand_id:
            product.brand = get_object_or_404(BrandCategory, id = brand_id)

        if main_category:
            product.main_cattegory.set()
        

        if not product.slug:
            product.slug = request.POST.get('slug')
        product.qunat = request.POST.get('qunat')

        product.is_sellprice = True if is_sellprice == 'on' or is_sellprice == 'True' else False
        product.active = True if active == 'on' or active == 'True' else False
        product.spessial = True if spessial == 'on' or spessial == 'True' else False
        product.have = True if have == 'on' or have == 'True' else False


        sell_price = request.POST.get('sell_price')
        if sell_price:
            product.sell_price = sell_price

        product.save()

# 
        spec_keys = request.POST.getlist('spec_keys[]')
        spec_values = request.POST.getlist('spec_values[]')
 
        for key_id, value in zip(spec_keys, spec_values):
            if key_id and value:
                try:
                    key_obj = ProductDetaKeys.objects.get(id=key_id)
                    ProductKeyValues.objects.get(product=product,key=key_obj).delete()
                    ProductKeyValues.objects.create(
                        product=product,
                        key=key_obj,
                        value=value
                    ) 
                except ProductDetaKeys.DoesNotExist:
                    continue


        check_price_and_notify(request)

        
        notification_in_edit_product_price_or_sell_price(product.pk,shop_id,'edit_sell_price' if sell_price else 'edit_price')
        

        if check_collabrator(request, shop_id):
            create_activity(request, 'افزودن محصول جدید مرحله 1', product.pk, 'ADD', shop_id)


        messages.success(
            request, 'ویرایش محصول موفقیت امیز بود!'
        )
        return redirect('pro:products_list',shop_id)

    else:
        context = {
            'super_categories': SuperCategory.objects.all(),
            'main_categories': MainCategory.objects.all(),
            'colors': ColorCategory.objects.all(),
            'brands': BrandCategory.objects.all(),
            'spec_keys': ProductDetaKeys.objects.all(),
            'product_key_value':ProductKeyValues.objects.filter(product=product),
            'shop_id':shop_id,
            'product':product
        }
        return render(
            request, 
            'shop_manage_products/product_edit.html',
              context
        )



def filter_product(request, shop_id):
    products = Products.objects.filter(shop__id=shop_id)

    filter_ss = request.GET.get('filter_ss')
    category_id = request.GET.get('category')
    main_category_id = request.GET.get('main_category')
    filter_v = request.GET.get('filter_v')
    inventory = request.GET.get('inventory')


    if inventory:
        if inventory == '2':
            return render(
                request,
                'shop_manage_products/products_list.html',
                {
                    'products':products.filter(qunat__lte=int(inventory))  
                }
            )  


    filtered_products = products   
    if category_id:
        filtered_products = filtered_products.filter(
            category__id=category_id,
            shop__id=shop_id
        )

    if main_category_id:
        filtered_products = filtered_products.filter(
            main_cattegory__id=main_category_id,
            shop__id=shop_id
        )

    if filter_ss:
        if filter_ss == 'best_selling_products':
            filtered_products = filtered_products.annotate(
                total_sales=Count('reservations')  # فرض بر اینکه related_name در ReservationModel هست
            ).order_by('-total_sales')[:6]

        elif filter_ss == 'populer':
            filtered_products = filtered_products.annotate(
                avg_rating=Avg('product__rating')  # 'product' همان related_name در Comments
            ).order_by('-avg_rating')

        elif filter_ss == 'in_cart_products':
            filtered_products = filtered_products.filter(
                id__in=Cart.objects.filter(product__shop__id=shop_id).values_list('product_id', flat=True)
            )

        elif filter_ss == 'in_watchlist_products':
            filtered_products = filtered_products.filter(
                id__in=WatchList.objects.filter(product__shop__id=shop_id).values_list('product_id', flat=True)
            )

        elif filter_ss == 'coupon_products':
            coupon_product_ids = []
            for coupon in Coupon.objects.filter(shop__id=shop_id):
                for product_item in filtered_products:
                    if product_item.main_cattegory == coupon.category:
                        coupon_product_ids.append(product_item.pk)
            filtered_products = filtered_products.filter(id__in=coupon_product_ids)

        elif filter_ss == 'uncoupon_products':
            coupon_product_ids = []
            for coupon in Coupon.objects.filter(shop__id=shop_id):
                for product_item in filtered_products:
                    if product_item.main_cattegory == coupon.category:
                        coupon_product_ids.append(product_item.pk)
            filtered_products = filtered_products.exclude(id__in=coupon_product_ids)


    if filter_v:
        if filter_v == 'lte_from_5':
            filtered_products = filtered_products.filter(
                active=True, qunat__lt=5
            )

        elif filter_v == 'spessial':
            filtered_products = filtered_products.filter(
                shop__id=shop_id, spessial=True
            )

        elif filter_v == 'actives':
            filtered_products = filtered_products.filter(
                shop__id=shop_id, active=True
            )

        elif filter_v == 'is_avb':
            filtered_products = filtered_products.filter(
                shop__id=shop_id, have=True
            )


    return render(
        request, 
        'shop_manage_products/products_list.html',
        {
            'products': filtered_products,
            'super_category':SuperCategory.objects.all(),
            'shop_id':shop_id,
        }
    )
