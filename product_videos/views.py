from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Products
from .models import ProductVideo
from django.contrib import messages
from sellers.models import Shop
from collaborator.views import check_collab_and_jobs



def add_video(request,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)


    if not request.user.is_authenticated:
        return redirect('acc:pro')
    

    if not check_collab_and_jobs(request, 'product_video_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    if request.method == 'POST':
        products = Products.objects.filter(id__in=request.POST.getlist('product_ids'),shop = shop)

        pv = ProductVideo.objects.create(
            shop = shop,
            title = request.POST.get('title'),
            video_file = request.FILES.get('video_file')
        )

        pv.products.add(*products)
        pv.save()

        messages.success(
            request,
            'ویدیو محصول با موفقیت اپلود شد!'
        )
        return redirect('pvideo:list_videos',shop_id)



def remove_video(request,video_id,shop_id):
    shop = get_object_or_404(Shop,id= shop_id)
    video = get_object_or_404(ProductVideo,id=video_id,shop = shop,shop__id = shop_id)

    if not check_collab_and_jobs(request, 'product_video_permissions', shop_id):
        messages.warning(
            request,    
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    video.delete()
    messages.success(
        request,
        'ویدیو محصول با موفقیت حذف شد!'
    )
    return redirect('pvideo:list_videos',shop_id)



def edit_product_video(request,video_id,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)
    pv=get_object_or_404(ProductVideo,id = video_id,shop = shop)

    if not check_collab_and_jobs(request, 'product_video_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    if request.method == 'POST':
        pv.title = request.POST.get('title')
        video_file = request.FILES.get('video_file')

        if video_file:
            pv.video_file = video_file
            
        pv.products.set(Products.objects.filter(id__in=request.POST.getlist('product_ids')))

        messages.success(
            request,
            'ویدیو محصول شما با موفقیت اپدیت شد!'
        )
        return redirect('pvideo:list_videos',shop_id)



def list_videos(request,shop_id):
    if not request.user:
        return redirect('acc:pro')
    
    if not check_collab_and_jobs(request, 'product_video_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    

    product_video=ProductVideo.objects.filter(
        shop = get_object_or_404(Shop,id = shop_id),
    )

    return render(
        request,
        'product_videos/list_videos.html',
        {
            'videos':product_video,
            'products':Products.objects.filter(shop__id=shop_id,active=True),
            'video_count':product_video.count()
        }
    )