from django.shortcuts import render,redirect
from django. contrib import messages
from django.db.models import Q
from reservations.models import Reservation
from .models import Products, Comments
from .product_session import viewsProduct
from django.http import JsonResponse, HttpResponseNotFound
from charts.models import ProductPriceHistory
from sellers.models import Shop  
from accaunts.check_auth import check_user
from django.db.models import Q,When,Case,Value,IntegerField
from django.shortcuts import get_object_or_404
from smartgtp.viewed import ViewedProducts
from .search_history import SearchHistory
from .models import BrandCategory,ProductKeyValues,ColorCategory
from .models import MainCategory,SuperCategory
from question_response.models import Response
from story.models import Story
from chat.share_list import shareable_list
from django.db.models import Avg
from follow.views import count_followers
from sellers.models import ShopRate
from product_videos.models import ProductVideo
from cart.models import Cart
from gallery_products.models import GalleryItem
from follow.check_follow import checkFollow
from notifications.shop_notification import notification_in_new_comment
from django.db.models import Avg 
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
from siteinfo.models import PromotionalProductsSlide



def index(request):
    shop_list = []
    category = SuperCategory.objects.all()



    for shop in Shop.objects.filter(active=True,reported=False):
        if request.user.is_authenticated:
            is_following = checkFollow(request,shop.pk,request.user.pk)
        else:
            is_following = False

        shop_data = {
            'name_shop': shop.name_shop,
            'id': shop.pk,
            'pk':shop.pk,
            'logo': shop.logo,
            'description':shop.description,
            'is_following':is_following,
            'shop':shop
        }
        shop_list.append(shop_data)

    
    return render(
        request,
        'shop/index.html',
        {
            'categorys':category,
            'best_shops':shop_list,
            'category':SuperCategory.objects.all()[:4],
            'brands':BrandCategory.objects.all()[:4],
            'products':Products.objects.filter(is_sellprice=True,active = True)[:9],
            'PromotionalProductsSlide':PromotionalProductsSlide.objects.all()
        }
    )



def best_shops(request):
    shop_list = []

    for shop in Shop.objects.all():
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
            'description':shop.description,
            'shop_rate': avg_rating,
            'full_stars': range(full_stars),
            'half_star': half_star,
            'empty_stars': range(empty_stars),
            'is_following':is_following,
        }
        shop_list.append(shop_data)

    return render(
        request,
        'shop/best_shops.html',
        {
            'shops': shop_list,
            
        }
    )



def product_detail(request, slug, id):
    from smartgtp.views import get_exemple_products

    product = get_object_or_404(Products, slug=slug, id=id)
    
    filtered_products = Products.objects.filter(active = True)
    ViewedProducts(request).add(id)
    viewsProduct(request, id)

    if product.qunat == 0:
        product.have = False
        product.save()


    following_staff = checkFollow(request,product.shop.pk,request.user.pk) if request.user.is_authenticated else False

    
    related = get_exemple_products(request,[product.pk])
    related_color = filtered_products.filter(color = product.color)
    related_brand = filtered_products.filter(brand = product.brand)
    

    one_year_ago = timezone.now().date() - timedelta(days=365)
    price_history = ProductPriceHistory.objects.filter(
        product=product, 
        date__gte=one_year_ago
    ).order_by('date')
    
    chart_data = {
        'labels': [],
        'prices': [],
        'sell_prices': []
    }
    
    for history in price_history:
        chart_data['labels'].append(history.date.strftime('%Y-%m-%d'))
        chart_data['prices'].append(float(history.price))
    
    product_videos=ProductVideo.objects.filter(products__id = id)

    return render(
        request, 
        'shop/product_detail.html', 
        {
            'product': product,
            'comments': Comments.objects.filter(product__id=id)[:4],
            'get_related_products': related.distinct(),
            'related_color':related_color,
            'related_brand':related_brand,
            'recommended_products': Products.objects.filter(id__in=ViewedProducts(request).get() ).exclude(id=id)[:6],
            'responses': Response.objects.filter(reply_ques__product__id=product.pk,reply_ques__responsed = True),
            'product_details': ProductKeyValues.objects.filter(product=product),
            'videos':product_videos,
            'len_videos':product_videos.count(),
            'gallery':GalleryItem.objects.filter(gallery_product__product__id = id),
            'price_history':ProductPriceHistory.objects.filter(product__id = id),
            'following_staff':following_staff,
            'price_history_json': json.dumps(chart_data),
            'cart':Cart.objects.filter(user=request.user,product=product)
        }
    )



def comment_add(request,id):
    user = check_user(request)
    product = Products.objects.get(id=id)


    if not user:
        messages.warning(
            request,
            'ابتدا وارد حساب خود شوید'
        )
        return redirect('acc:login')
    
    
    if request.method == 'POST':
        if not Reservation.objects.filter(order__user=user,paid = True,product= product,).exists():
            messages.error(
                request,
                'فقط کاربرانی که این محصول را خریده‌اند می‌توانند نظر بدهند.'
            )
            return redirect('product_detail',id,product.slug)


        else:
            new_comment = Comments(
                product=product,
                user=user,
                message=request.POST.get('message'),
                rating=request.POST.get('rating')
            )

            new_comment.save()

            notification_in_new_comment(new_comment.pk)

            messages.success(
                request, 
                'کامت شما ثبت شد ! ممنون از ثبت نظر شما'
            )
            return redirect('product_detail',id,product.slug)
    else:
        return HttpResponseNotFound()



def product_price_history(request, product_id):
    try:
        product = Products.objects.get(pk=product_id)
    except (Products.DoesNotExist):
        raise HttpResponseNotFound()

    return JsonResponse(
        {
            'product': product.name,
            'price_history': list(ProductPriceHistory.objects.filter(product=product,).order_by('date').values('date', 'price'))
        }
    )



def products_list(request):
    products = Products.objects.filter(active=True).order_by('-created')
    
    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            products
        )
    )
   


def context_send_html(request,products):
    return {
        'products' :products,
        'len':products.count(),
        'main_categorys':MainCategory.objects.all(),
        'categorys':SuperCategory.objects.all(),
        'brand':BrandCategory.objects.all(),
        'color':ColorCategory.objects.all(),
        'search_his':SearchHistory(request).search_history(),
        'chat_homes':shareable_list(request),
        'rates':Comments.objects.filter(product__active=True),
        'storys':Story.objects.all(),        
    }



def filter_products(request):
    filtered_products = Products.objects.all()

    sort_option = request.GET.get('sort')
    sell_price_filter = request.GET.get('sellprice')
    low_price_filter = request.GET.get('low_price')
    high_price_filter = request.GET.get('high_price')
    special_filter = request.GET.get('spessial')
    availability_filter = request.GET.get('is_avb')
    selected_color_id = request.GET.get('color')
    selected_brand_id = request.GET.get('brand')
    selected_category_id = request.GET.get('category')
    selected_main_category_id = request.GET.get('main_cate')

    if low_price_filter:
        filtered_products = filtered_products.filter(
            price__gte=low_price_filter
        )

    if high_price_filter:
        filtered_products = filtered_products.filter(
            price__lte=high_price_filter
        )

    if sell_price_filter == 'on':
        filtered_products = filtered_products.filter(
            is_sellprice=True
        )

    if special_filter == 'on':
        filtered_products = filtered_products.filter(
            spessial=True
        )

    if availability_filter == 'on':
        filtered_products = filtered_products.filter(
            have=True
        )

    if selected_color_id:
        filtered_products = filtered_products.filter(
            color__id=selected_color_id
        )

    if selected_brand_id:
        filtered_products = filtered_products.filter(
            brand__id=selected_brand_id
        )

    if selected_category_id:
        p_key_values = ProductKeyValues.objects.filter(product__category__id=selected_category_id).values_list('product_id', flat=True)
        filtered_products = filtered_products.filter(
            id__in=p_key_values
        )

    if selected_main_category_id:
        # ابتدا محصولاتی که در دسته‌بندی اصلی انتخابی هستند را پیدا کنید
        products_in_category = Products.objects.filter(
            main_cattegory__id=selected_main_category_id
        )
        
        # سپس ProductKeyValues مرتبط با این محصولات را بگیرید
        p_key_values = ProductKeyValues.objects.filter(
            product__in=products_in_category
        ).values_list('product_id', flat=True).distinct()
        
        # در نهایت محصولات را فیلتر کنید
        filtered_products = filtered_products.filter(id__in=p_key_values)



# class ProductKeyValues(models.Model):
#    product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='details')
#    key = models.ForeignKey('ProductDetaKeys',on_delete=models.CASCADE,null=True,blank=True) 
#    value = models.CharField(max_length=200)                                                                                                                
# class Products(models.Model):
#       name = models.CharField(_('نام  '),max_length=20)
#       description = models.TextField(_('توضیحات'),)
#       image = models.ImageField(_('1  575x575-عکس'),upload_to='media/product_images')
#       price = models.IntegerField(_('قیمت'))
#       sell_price = models.IntegerField(null=True,blank=True)
#       description_seo = models.CharField(_('توضیحات سئو سایت'),max_length=80, null=True,blank=True)
         
#       category = models.ForeignKey('SuperCategory',on_delete=models.CASCADE,null=True,blank=True)
#       main_cattegory = models.ManyToManyField('MainCategory')    
#     if selected_main_category_id:
        # p_key_values = ProductKeyValues.objects.filter(product__main_category__id=selected_main_category_id).values_list('product_id', flat=True)
        # filtered_products = filtered_products.filter(
        #     id__in=p_key_values
        # )   در هنگام فیلتر ارور میده

    if sort_option:
        if sort_option == 'time_old':
            filtered_products = filtered_products.order_by(
                'created'
            )

        elif sort_option == 'newest':
            filtered_products = filtered_products.order_by(
                '-created'
            )

        elif sort_option == 'highest_price':
            filtered_products = filtered_products.order_by(
                '-price'
            )

        elif sort_option == 'lowest_price':
            filtered_products = filtered_products.order_by(
                'price'
            )

    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            filtered_products.distinct()
        )
    )



def like_or_dis_like_prodcut(request,product_id):
    user = check_user(request)
    product=get_object_or_404(Products,id = product_id)

    if not user:
        messages.error(
            request,'لاگین نکرده نمیتوانید محصول را لایک کنید!'
        )
    
    if user in product.like.all():
        product.like.remove(user)
        status = 'DISLIKE'
    else:
        product.like.add(user)
        status = 'LIKE'

    return JsonResponse(
        {
            'like_status':status,
            'like_count':product.like.count()
        }
    )



def search_products(request):

    query=request.GET.get('q','').strip()
    results = []
    SearchHistory(request).add(text=query)

    if query:
        combined_filter = (
            Q(name__icontains=query)|
            Q(description__icontains=query)|
            Q(description_seo__icontains=query)
        )
        results = Products.objects.filter(combined_filter).annotate(
            relevance = Case(
                When(
                    name__icontains = query,
                    then=Value(3),
                ),
                When(
                    description__icontains = query,
                    then=Value(2),
                ),
                When(
                    description_seo__icontains = query,
                    then=Value(1),
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-relevance')


        return render(
            request,
            'shop/products.html',
            context_send_html(
                request,
                results
            )
        )

    else:return HttpResponseNotFound()

 

def super_category(request):
    
    categories = SuperCategory.objects.all()
    main_categories = MainCategory.objects.all()
    return render(
        request,
        'shop/super_category.html',
        {
            'category': categories,
            'main_categories': main_categories, 
            'category':SuperCategory.objects.all(),
            'main_category':MainCategory.objects.all()[:14],
            'brands':BrandCategory.objects.all(),
            'products':Products.objects.all(),
        }
    )



def super_category_products(request,super_category_id,slug):
    super_category = get_object_or_404(SuperCategory,id = super_category_id)
    
    return render(
        request,
        'shop/products.html',
        context_send_html(
            request,
            Products.objects.filter(category = super_category,active = True)        
        )
    )



@csrf_exempt
def get_main_categories(request, super_category_id):
    if request.method == 'GET':
        main_categories = MainCategory.objects.filter(super_category_id=super_category_id)
        print(main_categories)
        categories_data = []
        for category in main_categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'slug':category.slug,
                'short_des': category.short_des,
                'icon': category.icon,
                'image': category.image.url if category.image else None,
            })
        
        return JsonResponse(categories_data, safe=False)



def main_category_detail(request,slug):    
    main_category = get_object_or_404(MainCategory,slug = slug)
    products = Products.objects.filter(main_cattegory__slug = slug,active = True)
    return render(
        request,
        'shop/products.html',
        {
            'products':products,
            'len':products.count(),
            'categorys':MainCategory.objects.filter(
                super_category__id = main_category.super_category.pk
            ),
            'page_title':main_category,
            'brand':BrandCategory.objects.all(),
            'color':ColorCategory.objects.all(),
            'search_his':SearchHistory(request).search_history(),
            'chat_homes':shareable_list(request),
            'rates':Comments.objects.filter(product__active=True),
            'storys':Story.objects.all(), 
        },
    )



def brand_detail(request,id,slug):
    brand=get_object_or_404(BrandCategory,slug=slug,id=id)
    
    return render(
        request,
        'shop/products.html',
        {
            'products':Products.objects.filter(brand__slug = slug,active = True),
            'categorys':BrandCategory.objects.all(),
            'page_title':brand,
            'brand':BrandCategory.objects.all(),
            'color':ColorCategory.objects.all(),
            'search_his':SearchHistory(request).search_history(),
            'chat_homes':shareable_list(request),
            'rates':Comments.objects.filter(product__active=True),
            'storys':Story.objects.all(), 
        }
    )
