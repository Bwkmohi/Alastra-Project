from django.shortcuts import render,get_object_or_404 ,redirect
from reservations.models import OrderModel,Reservation
from django.contrib import messages
from sellers.check import get_shop
from facelogin.views import check_secure_and_enter_password
import openpyxl
from django.http import HttpResponse
from sellers.models import Shop
from django.utils import timezone
from reservations.models import ProvinceCategory,Citys
from shop.models import Products
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Count
from django.shortcuts import render
from collaborator.views import check_collabrator,check_collab_and_jobs
from collaborator.views import create_activity
from notifications.user_notification import reserv_status
from django.utils import timezone
from datetime import datetime, time
from sellers.check import check_is_seller



def orders_list_context(request,shop_id,res):
    return {
        'orders': res,
        'shop_products':Products.objects.filter(
            id__in=Reservation.objects.filter(shop__id=shop_id,paid=True,canceled=False).values_list(
                'product__id',flat=True
            )),
        'province':ProvinceCategory.objects.filter(
            id__in=Reservation.objects.filter(
                    shop__id=shop_id,paid=True,canceled=False
                ).values_list('order__province__id',flat=True)
        ),
        'citys':Citys.objects.all(),
        'shop_id':shop_id,
    }



def filter_reservs(request, shop_id):
    reservations = Reservation.objects.filter(paid=True,shop__id=shop_id,canceled=False)

    filter_by_province = request.GET.get('filter_by_province')
    filter_by_city = request.GET.get('filter_by_citys')
    # filter_reserv_staff = request.GET.get('filter_reserv_staff')
    filtered_reservations = reservations


    # if filter_by_time:
    #     now = timezone.now()

    #     if filter_by_time == 'today':
    #         start_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    #         end_day = start_day + timedelta(days=1)
    #         filtered_reservations = filtered_reservations.filter(
    #             order__created_at__gte=start_day,
    #             order__created_at__lt=end_day,
    #         )

    #     elif filter_by_time == 'yesterday':
    #         pass

    #     elif filter_by_time == 'this_week':
    #         start_of_week = now - timedelta(days=now.weekday())
    #         start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    #         end_of_week = start_of_week + timedelta(days=7)
    #         filtered_reservations = filtered_reservations.filter(
    #             order__time__gte=start_of_week,
    #             order__created_at__lt=end_of_week,
    #         )

    #     elif filter_by_time == 'last_week':
    #         pass

    #     elif filter_by_time == 'this_month':
    #         if now.month == 12:
    #             start_of_next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    #         else:
    #             start_of_next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    #         start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    #         filtered_reservations = filtered_reservations.filter(
    #             order__created_at__gte=start_of_month,
    #             order__created_at__lt=start_of_next_month,
    #         )

    #     elif filter_by_time == 'last_month':
    #         pass


    # if filter_reserv_staff:
    #     if filter_reserv_staff == 'is_sent':
    #         filtered_reservations = filtered_reservations.filter(
    #             sent_to_post=True
    #         )

    #     elif filter_reserv_staff == 'canceled':
    #         filtered_reservations = filtered_reservations.filter(
    #             canceled=True
    #         )

    #     elif filter_reserv_staff == 'delivered':
    #         filtered_reservations = filtered_reservations.filter(
    #             delivered=True
    #         )

    #     elif filter_reserv_staff == 'checked':
    #         filtered_reservations = filtered_reservations.filter(
                    
    #         )


    if filter_by_province:
        province_obj = get_object_or_404(ProvinceCategory, id=filter_by_province)
        filtered_reservations = filtered_reservations.filter(
            order__province=province_obj
        )
        print(filtered_reservations)
    if filter_by_city:
        filtered_reservations = filtered_reservations.filter(
            order__city=filter_by_city
        )
        print(filtered_reservations)

    print(filtered_reservations)
    return render(
        request,
        'shop_manage_order/orders_list.html',
        orders_list_context(
            request,
            shop_id,
            filtered_reservations
        )
    )
         

 
def orders_list(request,shop_id):

    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    
    if check_collab_and_jobs(request,'can_see_orders',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
     
   
    reservs = Reservation.objects.filter(
        order__paid =True,
        shop__id = get_shop(request,shop_id).pk,
        delivered = False,
        sent_to_post=False,
        paid = True,
        canceled=False
    ).order_by('order__created_at')
 

    return render(
        request,
        'shop_manage_order/orders_list.html',
        orders_list_context(
            request,
            shop_id,
            reservs
        )
    )



def list_filtered_orders(request,shop_id,type_filter):

    if check_collab_and_jobs(request,'can_see_orders',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    reservs = Reservation.objects.filter(
        order__paid =True,
        shop__id = get_shop(request,shop_id).pk,
        paid = True,
    )


    if type_filter == 'sended':
        filtered_reservs = reservs.filter(
            sent_to_post = True
        )


    elif type_filter == 'unsended':
         filtered_reservs = reservs.filter(
            sent_to_post = False
        )
         

    elif type_filter == 'canceled':
        filtered_reservs = reservs.filter(
            canceled=True
        ).distinct()


    elif type_filter == 'today':
        start_of_day = timezone.make_aware(datetime.combine(timezone.now().date(), time.min))
        end_of_day = timezone.make_aware(datetime.combine(timezone.now().date(), time.max))

        filtered_reservs = reservs.filter(
            order__created_at__gte=start_of_day, 
            order__created_at__lte=end_of_day
        )


    return render(
        request,
        'shop_manage_order/orders_list.html',
        orders_list_context(
            request,
            shop_id,
            filtered_reservs.distinct()
        )
    )




def update_reserv_detail(request, shop_id, id):

    shop = get_shop(request, shop_id)
    reserv = get_object_or_404(Reservation, id=id, shop=shop)
    

    if not check_collab_and_jobs(request, 'edit_orders', shop_id):
        messages.warning(request, 'شما به این بخش دسترسی ندارید!')
        return redirect('')


    if request.method == 'POST':
        tracking_code = request.POST.get('tracking_code')

        preparation = request.POST.get('preparation') == 'True'
        sent_to_post = request.POST.get('sent_to_post') == 'True'
        post_delivery = request.POST.get('post_delivery') == 'True'
        delivered = request.POST.get('delivered') == 'True'



        if check_collabrator(request, shop_id):
            create_activity(request, 'ویرایش جزییات سفارش', reserv.pk, 'EDIT', shop_id)
        else:
            if not check_is_seller(request):
                return redirect('acc:pro')
        print(f"preparation: {preparation}, sent_to_post: {sent_to_post}, post_delivery: {post_delivery}, delivered: {delivered}")

        print(reserv.preparation)

        if preparation:
            reserv.preparation = True
            reserv.save()
            reserv_status(reserv.pk)

        if sent_to_post:
            reserv.sent_to_post = True
            reserv.save()
            reserv_status(reserv.pk)


        if post_delivery:
            reserv.post_delivery = True
            reserv.save()
            reserv_status(reserv.pk)

        if delivered:
            reserv.delivered = True
            reserv.save()
            reserv_status(reserv.pk)
        
        print(f"preparation: {preparation}, sent_to_post: {sent_to_post}, post_delivery: {post_delivery}, delivered: {delivered}")

        
        messages.success(
            request,
            'وضیعت سفارش آپدیت شد!'
        )
        return redirect('ord:orders_list', shop_id)



def archive_list(request,shop_id):

    if check_collab_and_jobs(request,'can_see_orders',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    archives = (
        Reservation.objects
        .annotate(year=ExtractYear('order__created_at'), month=ExtractMonth('order__created_at'))
        .values('year', 'month')
        .annotate(count=Count('id'))
        .order_by('-year', '-month')
    )


    return render(
        request,
        'shop_manage_order/archive_list.html',
        {
            'archives': archives,
            'shop_id':shop_id,
        }
        )



def order_archive_detail(request,shop_id, year, month=None):

    if check_collab_and_jobs(request,'can_see_orders',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    if month:
        orders = OrderModel.objects.filter(
            created_at__year=year,
            created_at__month=month
        )


    else:
        orders = OrderModel.objects.filter(
            created_at__year=year
        )


    return render(
        request,
        'shop_manage_order/archive_detail.html',
        {
            'orders': orders,
            'year': year,
            'month': month,
            'shop_id':shop_id,
        }
    )



def export_orders_for_seller(request, shop_id):
    
    if check_collab_and_jobs(request,'can_see_orders',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    try:
        shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
        return HttpResponse("فروشگاه پیدا نشد.", status=404)
 

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Orders - {shop.name_shop}"


    ws.append(
        [
            'شماره سفارش',
            'نام محصول',
            'ای دی کاربر',
            'ای دی محصول',
            'تعداد', 
            'نام گیرنده',
            'نام خانوادگی',
            'شماره تلفن گیرنده',
            'ادرس',
            'استان',
            'شهر',
            'کد پستی',
            'کدپیگیری',
            'نام فروشگاه',
            'دریافت شده',
            'لغو ارسال ',
            'قیمت کل', 
            'تاریخ سفارش'
        ]
    )


    for r in Reservation.objects.filter(
        shop=shop,paid=True
    ).select_related('order', 'product'):
        

        ws.append(
            [
                r.pk,
                r.product.name,
                r.order.user.pk,
                r.product.pk,
                r.quantity if hasattr(r, 'quantity') else '1',  
                r.order.name,
                r.order.lastname,
                r.order.phone,
                r.order.address,
                r.order.province.name,
                r.order.city.name,
                r.order.postaddress,
                r.order.tracking_code ,
                r.shop.name_shop,
                'بله' if r.delivered == True else 'خیر',
                r.canceled ,
                r.order.total_price,
                r.order.created_at.strftime('%Y-%m-%d'),
            ]
        )

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    filename = f'orders_{shop.name_shop}_{timezone.now().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'

    wb.save(response)
    return response