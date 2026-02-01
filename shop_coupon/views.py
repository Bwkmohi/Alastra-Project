from django.shortcuts import render,get_object_or_404 ,redirect
from django.contrib import messages
from copon2.models import Coupon
from sellers.check import get_shop
from shop.models import MainCategory
from facelogin.views import check_secure_and_enter_password
from collaborator.views import check_collabrator,create_activity,check_collab_and_jobs
from django.http import Http404



def coupon_list(request,shop_id):

    if check_collab_and_jobs(request,'see_coupons',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    if check_secure_and_enter_password(request,'self_function_checking') == True:
        url = f'{request.path}'.replace('/','%')
        return redirect('enter_password',redirect_url=f'{url}')
    

    coupon = Coupon.objects.filter(
        shop= get_shop(request,shop_id)
    )
    
    
    return render(
        request,
        'shop_coupon/coupons_list.html',
        {
            'coupon':coupon,
            'len':coupon.count(),
            'shop_id':shop_id,
            'main_category':MainCategory.objects.all()
            }
        )



def coupon_add(request, shop_id):

    if not check_collab_and_jobs(request, 'coupon_add', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    if request.method == 'POST':

        category_id = request.POST.get('category')
        code = request.POST.get('code')

        if Coupon.objects.filter(code__iexact=code).exists():
            messages.warning(
                request,
                'چنین کد کوپنی از قبل وجود دارد. لطفا کد دیگری را استفاده کنید!'
            )
            return redirect('cou:coupon_list',shop_id)
        
        coupon = Coupon.objects.create(
            code=code,
            value=request.POST.get('value'),
            usage_limit=request.POST.get('usage_limit'),
            valid_from=request.POST.get('valid_from'),
            valid_to=request.POST.get('valid_to'),
            shop=get_shop(request, shop_id)
        )
        
        coupon.is_percent = bool(request.POST.get('is_percent'))
        coupon.active = bool(request.POST.get('active'))
        coupon.for_followers = bool(request.POST.get('for_followers'))
        coupon.save()

        if category_id:
            coupon.category = MainCategory.objects.get(id=category_id)
            coupon.save()

        if check_collabrator(request, shop_id):
            create_activity(
                request, 'افزودن کوپن جدید', coupon.pk, 'ADD', shop_id
            )

        messages.success(
            request,
            'کوپن تخفیف شما با موفقیت ثبت شد'
        )
        return redirect('cou:coupon_list', shop_id)

 
    raise Http404("صفحه یا شیء مورد نظر پیدا نشد")



def coupon_delete(request,id,shop_id):
    coupon=get_object_or_404(Coupon,id=id,shop = get_shop(request,shop_id))
    

    if check_collab_and_jobs(request,'coupon_remove',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)

    
    if not check_collabrator(request,shop_id):
        pass
    else:
        create_activity(
            request,'حذف کوپن',coupon.pk,'REMOVE',shop_id
        )


    coupon.delete()

    messages.success(
        request,
        'حذف کوپن موفقیت امیز'
    )
    return redirect('cou:coupon_list',shop_id)



def coupon_edit(request, shop_id, id):
    coupon = get_object_or_404(Coupon, id=id)


    if not check_collab_and_jobs(request, 'coupon_edit', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)

    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')

        coupon.code = request.POST.get('code')
        coupon.value = request.POST.get('value')
        coupon.usage_limit = request.POST.get('usage_limit')
        coupon.is_percent = bool(request.POST.get('is_percent'))
        coupon.active = bool(request.POST.get('active'))
        coupon.for_followers = bool(request.POST.get('for_followers'))

        if valid_from:
            coupon.valid_from = valid_from
        if valid_to:
            coupon.valid_to = valid_to

        coupon.save()

        if category_id:
            coupon.category = MainCategory.objects.get(id=category_id)
            coupon.save()

        if check_collabrator(request, shop_id):
            create_activity(request, 'ویرایش کوپن', coupon.pk, 'EDIT', shop_id)

        messages.success(
            request, 
            'کوپن تخفیف شما با موفقیت ثبت شد'
        )
        return redirect('cou:coupon_list', shop_id)
    raise Http404("صفحه یا شیء مورد نظر پیدا نشد")