from django.shortcuts import render,get_object_or_404 ,redirect
from shop.models import Products,Comments
from django.contrib.auth.models import User
from .models import Shop,Seller
from reservations.models import OrderModel,Reservation
from django.contrib import messages
from .check import check_is_seller,check_seller_shop
from django.db.models import Count, Avg,Sum
from django.utils import timezone
from charts.models import MonthlyProfit
from datetime import datetime, timedelta
from .check import get_shop
from facelogin.views import check_secure_and_enter_password
from collaborator.views import check_collabrator
from accaunts.check_auth import check_user_authentication,check_user
from siteinfo.views import create_user_and_shop_image
from django.utils.timezone import now
from accaunts.models import UserAuthentication
from follow.check_follow import checkFollow
from follow.views import count_followers
from story.models import Story
from .models import ShopRate
from .models import Shop
from django.db.models import Count, Q
from django.shortcuts import render
from follow.models import FolloweUnFollow
from collections import Counter


def seller_dashbord(request):
    seller = check_is_seller(request)
    reservations = Reservation.objects.filter(shop__seller=seller, paid=True)
    shops = Shop.objects.filter(seller = seller)

    if not seller:
        messages.error(request,'شما اجازه دسترسی به این صفحه را ندارید')
        return redirect('sellers:become_seller')
    

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')

    total_orders = Reservation.objects.count()

    # دسته‌بندی وضعیت‌ها
    sent_count = Reservation.objects.filter(sent_to_post=True).count()
    delivered_count = Reservation.objects.filter(delivered=True).count()
    waiting_count = Reservation.objects.filter(
        preparation=True, canceled=False,delivered=False
    ).count()
    canceled_count = Reservation.objects.filter(
        canceled=True
    ).count()

    new_count = Reservation.objects.filter(paid=True).count()
    total = Reservation.objects.count()
    delivered = Reservation.objects.filter(delivered=True,paid=True).count()
    canceled = Reservation.objects.filter(canceled=True).count()
    pending = total if total else 0 - delivered if delivered else 0  - canceled

    circumference = 2 * 3.14 * 70
    if total and delivered:
        delivered_offset = circumference - (delivered / total) * circumference
    delivered_offset = 0
    
    if total and canceled:
        canceled_offset = circumference - (canceled / total) * circumference
    canceled_offset = 0

    if total and pending:
        pending_offset = circumference - (pending / total) * circumference
    pending_offset = 0
    
    shops_profit = []
    for shop in shops:
        total_profit = Reservation.objects.filter(
            shop=shop,
            paid=True,
            canceled=False
        ).aggregate(total=Sum('totalprice'))['total'] or 0

        shops_profit = []
        for shop in shops:
            reservs = Reservation.objects.filter(shop=shop,paid=True)
            total_profit = reservs.aggregate(total=Sum('totalprice'))['total'] or 0

            shops_profit.append({
                'shop': shop,
                'profit': total_profit,
                'orders_count':reservs.count(),
                'name_shop':shop.name_shop,
                'logo':shop.logo.url
            })


        # پیدا کردن بیشترین سود
        if shops_profit:
            max_profit = max(s['profit'] for s in shops_profit)
        else:
            max_profit = 1  # جلوگیری از تقسیم بر صفر

        # حالا درصد پیشرفت رو نسبت به max_profit محاسبه می‌کنیم
        for sp in shops_profit:
            sp['progress'] = int((sp['profit'] / max_profit) * 100) if max_profit else 0
            sp['profit_display'] = f"{sp['profit'] / 1_000_000:.1f}M"  
 
    list_men_count = 0
    list_women_count = 0
    list_unknown = 0


    for reservation in reservations:
        user = reservation.order.user.pk
        try:
            user_auth = UserAuthentication.objects.get(user__id=user)
            if user_auth.gender == 'MEN':
                list_men_count += 1
            elif user_auth.gender == 'WOMEN':
                list_women_count += 1
            else:
                list_unknown += 1
        except UserAuthentication.DoesNotExist:
            list_unknown += 1

    

    if shops.exists():
        shop = shops.first()
        province_distribution = get_province_distribution(shop)
    else:
        province_distribution = []
    

    if shops.exists():
        shop = shops.first()
        category_distribution = get_top_selling_categories(shop)
    else:
        category_distribution = []
    
    shops_followers = []
    max_followers = 1  # مقدار پیش فرض برای جلوگیری از تقسیم بر صفر

    if shops.exists():
        max_followers = max(FolloweUnFollow.objects.filter(shop=shop).count() for shop in shops) or 1

    for shop in shops:
        follower_count = FolloweUnFollow.objects.filter(shop=shop).count()
        height_percent = int((follower_count / max_followers) * 100) if max_followers else 0

        shops_followers.append({
            'name': shop.name_shop,
            'followers': follower_count,
            'height_percent': int(height_percent),
        })
    # 
    total_sales = Reservation.objects.filter(
        shop__seller=seller,
        paid=True
    ).aggregate(total=Sum('totalprice'))['total'] or 0
 
       
    return render(
        request,
        'sellers/seller_dashbord.html',
        {
            'shops':shops,
            'count_shops':shops.count(),
            'total_orders': total_orders,
            'sent_count': sent_count,
            'delivered_count': delivered_count,
            'waiting_count': waiting_count,
            'canceled_count': canceled_count,
            'new_count': new_count,
            'sent_percent': calc_percent(sent_count,total_orders),
            'delivered_percent': calc_percent(delivered_count,total_orders),
            'waiting_percent': calc_percent(waiting_count,total_orders),
            'canceled_percent': calc_percent(canceled_count,total_orders),
            'new_percent': calc_percent(new_count,total_orders),
            'total_orders': total,
            'delivered_offset': delivered_offset,
            'canceled_offset': canceled_offset,
            'pending_offset': pending_offset,
            # 
            'shops_profit': shops_profit,
            # 
            'men': list_men_count,
            'women': list_women_count,
            'unknown': list_unknown,
            'province_distribution': province_distribution[:5],
            'category_distribution': category_distribution[:5],
            # 
            'shops_followers': shops_followers,
            # 
            'total_sales':total_sales,
            'products_count':Products.objects.filter(shop__seller=seller,active=True).count(),
            'reservs_count':Reservation.objects.filter(paid = True,shop__seller=seller).count()
        }
    )



def calc_percent(count,total_orders):
    return round((count / total_orders) * 100, 1) if total_orders > 0 else 0



def get_province_distribution(shop):
    reservations = Reservation.objects.filter(shop=shop, paid=True)
    # شمارش استان‌ها
    province_counter = Counter()

    for reservation in reservations:
        province = reservation.order.province.name
        province_counter[province] += 1
    total = sum(province_counter.values()) or 1  

    distribution = []
    for province, count in province_counter.most_common():  
        percent = int((count / total) * 100)
        distribution.append({
            'name': province,
            'percent': percent
        })

    return distribution



def get_top_selling_categories(shop):
    reservations = Reservation.objects.filter(shop=shop, paid=True)
    category_counter = Counter()

    for reservation in reservations:
        product = reservation.product
        for cat in product.main_cattegory.all():
            category_counter[cat.name] += reservation.quantity

    total_sales = sum(category_counter.values()) or 1

    distribution = []
    for cat_name, count in category_counter.most_common():
        percent = int((count / total_sales) * 100)
        distribution.append({
            'name': cat_name,
            'percent': percent
        })

    return distribution



def shop_dashbord(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id, seller__is_seller=True)
    
    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')

    if not check_seller_shop(request, shop_id):
        if not check_collabrator(request, shop_id):
            messages.warning(request, 'شما به این بخش دسترسی ندارید!')
            return redirect('index')

    

    profits = MonthlyProfit.objects.filter(shop_id=shop_id).order_by('year', 'month')
    months = [f"{p.year}/{p.month}" for p in profits]
    profit_values = [p.total_profit for p in profits]

    total_sales_product = Reservation.objects.filter(
        shop__id=shop_id,
        order__paid=True
    ).count()

    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    buyers_with_orders_before = OrderModel.objects.filter(
        paid=True,
        created_at__lt=start_of_month
    ).values_list('user', flat=True).distinct()

    new_buyers_count = OrderModel.objects.filter(
        paid=True,
        created_at__gte=start_of_month
    ).exclude(user__in=buyers_with_orders_before).values('user').distinct().count()

    # 4. سود این ماه (جمع totalprice از رزروها)
    start_of_month = datetime(now().year, now().month, 1)

    monthly_profit = OrderModel.objects.filter(
        paid=True,
        created_at__gte=start_of_month
    ).aggregate(total_profit=Sum('total_price'))['total_profit'] or 0

    # 5. سود این هفته
    start_of_week = timezone.now() - timedelta(days=timezone.now().weekday())

    weekly_profit = OrderModel.objects.filter(
        paid=True,
        created_at__gte=start_of_week
    ).aggregate(total_profit=Sum('total_price'))['total_profit'] or 0

    # 7. محصولات پرفروش - تعداد فروش هر محصول
    top_products = Reservation.objects.filter(
        shop=shop_id,
        order__paid=True
    ).values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:10]

    labels = [item['product__name'] for item in top_products]
    data = [item['total_qty'] for item in top_products]

    # 8. تعداد برگشتی‌ها 
    returned_orders_count = OrderModel.objects.filter(
        paid=True,
    ).count()

    # 9. تعداد محصولات لغو ارسال شده (combace_reserv = True)
    cancelled_send_count = OrderModel.objects.filter(
    ).count()

    buyers = OrderModel.objects.filter(paid=True)
    buyers_with_order_counts = buyers.values('user').annotate(order_count=Count('id'))

    new_buyers_count1 = buyers_with_order_counts.filter(order_count=1).count()
    previous_buyers_count = buyers_with_order_counts.filter(order_count__gt=1).count()

    top_rated_products = Comments.objects.values('product__name').annotate(
        avg_rating=Avg('rating')
    ).order_by('-avg_rating')[:10]

    labels_rate = [item['product__name'] for item in top_rated_products]
    data_rate = [round(item['avg_rating'], 2) if item['avg_rating'] else 0 for item in top_rated_products]

    request.session['shop_id'] = shop.pk

    year=timezone.now().year
    print('year is :',year)

    profits = MonthlyProfit.objects.filter(shop_id=shop_id, year=year).order_by('month')
    
    total_profit = profits.aggregate(Sum('total_profit'))['total_profit__sum'] or 0
    avg_profit = total_profit / profits.count() if profits.count() > 0 else 0
    highest_profit = profits.first().total_profit if profits.exists() else 0


    last_orders = Reservation.objects.filter(shop__id = shop_id,paid = True,canceled=False,delivered=False).order_by('-order__created_at')[:3]

    context = {
        'total_sales_product': total_sales_product,
        'buyers_with_orders_before': buyers_with_orders_before,
        'shop': shop,
        'new_buyers_count': new_buyers_count,
        'monthly_profit': monthly_profit,
        'weekly_profit': weekly_profit,
        'top_products': top_products,
        'returned_orders_count': returned_orders_count,
        'cancelled_send_count': cancelled_send_count,
        'profit_values': profit_values,
        'months': months,
        'new_buyers_count1': new_buyers_count1,
        'previous_buyers_count': previous_buyers_count,
        'labels': labels,
        'data': data,
        'labels_rate': labels_rate,
        'data_rate': data_rate,
        'shop_id':shop_id,
        # 
        'profits': profits,
        'total_profit': total_profit,
        'avg_profit': avg_profit,
        'highest_profit': highest_profit, 
        'year': year,
        'shop_id': shop_id,
        'top_view_product':Products.objects.filter(shop__id = shop_id,active=True).order_by('-views'),
        'last_orders':last_orders
    }
    return render(request, 'sellers/shop_dashbord.html', context)



def save_shop_id_in_session(request,shop_id):
    request.session['shop_id'] = shop_id



def shop_products_rate(request,shop_id):
    return Products.objects.filter(shop=get_shop(request,shop_id)).annotate(
            avg_rating = Avg('product__rating')
    ).order_by('-avg_rating')[:6]



def shop_public_page(request,shop_id):
    category_list=[]
    shop=get_shop(request,shop_id)
    products=Products.objects.filter(shop=shop,active = True)

    if not shop:
        messages.warning(
            request,
            'فروشگاه مسدود شده است!'
        )
        return redirect('acc:pro')

    for i in products:
        category_list.append(
            i.category
        )
    
    if request.user.is_authenticated and shop:
        is_following = checkFollow(request,shop.pk,request.user.pk)
    else:
        is_following = False

    return render(
        request,
        'sellers/shop_public_page.html',
        {
            'shop':{
                'name_shop':shop.name_shop,
                'description':shop.description,
                'logo':shop.logo.url,
                'banner':shop.banner.url if shop.banner else '',
                'count_followers':count_followers(request,shop_id),
                'posts_count':products.count(),
                'rateing':'',
                'id':shop.id,
                'user':shop.seller.user

            },
            'is_following':is_following,
            'user_following_staff':'',
            'products':products,
            'categorys':category_list,
            'storys':Story.objects.filter(shop__id = shop_id)
        }
        )



def become_seller(request):
    user = check_user(request)
    seller = check_is_seller(request)
    user_authentication = check_user_authentication(request)

    if not user:
        messages.error(
            request,
            'ابتدا باید وارد حساب خود شوید'
        )
        return redirect('acc:login')
    print(seller)

    if seller is not None:
        return redirect('sellers:seller_dashbord')

    
    if not user_authentication:
        messages.error(
            request,
            ' باید هراز هویت کنید!'
        )
        return redirect('acc:authentication')
    

    Seller.objects.create(
        user=user,
        user_authentication=user_authentication,
    )
    messages.success(
        request,
        'اطلاعات شما با موفقیت ثبت شدند! بزودی تایید و بررسی خواهند شد!'
    )
    return redirect('sellers:create_shop') 



def create_shop(request):
    seller = check_is_seller(request)

    if not seller:
        return redirect('sellers:become_seller')
 
    if seller.shops.count() >= 3:
        messages.warning(request, "شما حداکثر تعداد مجاز ایجاد (۳ عدد) فروشگاه را دارید.")
        return redirect('sellers:seller_dashbord',) 
    
    if seller:
        if request.method == 'POST':
            logo = request.FILES.get('logo')
            banner = request.FILES.get('banner')
            status = bool(request.POST.get('active')),type(request.POST.get('active'))

            shop = Shop.objects.create(
                seller = seller ,
                name_shop=request.POST.get('name_shop'),
                description=request.POST.get('description'),
                logo=logo,
                banner = banner
            )

            if status == True:
                shop.active=True
                shop.save()
            else:
                shop.active=False
                shop.save()

            create_user_and_shop_image()
            save_shop_id_in_session(request,shop.pk)

            messages.success(
                request,'فروشگاه شما با موفقیت ایجاد شد!'
            )
            return redirect('sellers:shop_dashbord',shop.pk)
        
        else:
            return render(
                request,
                'sellers/create_shop.html',
                {
                    'seller':seller
                }
            )
        
    else:
        messages.success(
            request,
            'شما باید احراز هویت کنید'
        )
        return redirect('sellers:become_seller')



def shop_edit(request, shop_id):
    user = get_object_or_404(User,id = request.user.pk)
    shop = get_object_or_404(Shop, id=shop_id)


    if shop.seller.user != user:
        messages.error(
            request, 
            "شما اجازه ویرایش این فروشگاه را ندارید."
        )
        return redirect('index')  
    

    if request.method == 'POST':
        name_shop = request.POST.get('name_shop', '').strip()
        description = request.POST.get('description', '').strip()
        active = request.POST.get('active',[])
        logo = request.FILES.get('logo')  
        banner = request.FILES.get('banner')  

        shop.name_shop = name_shop
        shop.description = description
        shop.active = False if active == 'False' else True
        shop.save()

        if logo:
            shop.logo = logo
            shop.save()
        
        if banner:
            shop.banner = banner
            shop.save()

        messages.success(
            request, 
            "اطلاعات فروشگاه بروزرسانی شد."
        )
        return redirect('sellers:shop_dashbord', shop_id=shop_id)


    return render(
        request, 
        'sellers/shop_edit.html', 
        {
            'shop': shop,
            'shop_id':shop_id
        }
    )



def add_shop_rate(request):
    if request.method == 'POST':
        rate = request.POST.get('rate')
        reserv_id = request.POST.get('reserv_id')
        url = request.POST.get('url')

        if not ShopRate.objects.filter(reserv__id = reserv_id).exists():    
            ShopRate.objects.create(
                reserv = get_object_or_404(Reservation,id = reserv_id),
                rateing = rate,
            )
            messages.success(
                request,
                'امتیاز با موفقیت ثبت شد!'
            )
            return redirect(url)
        
        else:
            messages.warning(
                request,
                'قبلا امتیاز ثبت کردید!'
            )
            return redirect(url)



def shop_search(request):
    query = request.GET.get('q')   
    results = []
    shop_list = []


    if query:
        results = Shop.objects.filter(
            Q(name_shop__icontains=query) | Q(description__icontains=query),active = True,reported=False
        )


    for shop in results:
        avg_rating = ShopRate.objects.filter(reserv__shop=shop).aggregate(avg=Avg('rateing'))['avg'] or 0
        avg_rating = round(avg_rating, 1)

        full_stars = int(avg_rating)
        half_star = 1 if avg_rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        if request.user.is_authenticated:
            is_following = checkFollow(request,shop.pk,request.user.pk)
        else: is_following = False
        
        shop_data = {
            'name_shop': shop.name_shop,
            'shop_products_count': shop.shop_products_count(),
            'id': shop.pk,
            'count_followers': count_followers(request, shop.pk),
            'logo': shop.logo,
            'shop_rate': avg_rating,
            'full_stars': range(full_stars),
            'half_star': half_star,
            'empty_stars': range(empty_stars),
            'is_following':is_following,
            'products': Products.objects.filter(shop__id = shop.pk)[:3]
        }
        shop_list.append(shop_data)

    return render(
        request, 
        'shop/best_shops.html',
        {
            'shops': shop_list,
        }
    )