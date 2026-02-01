from django.shortcuts import render,get_object_or_404,redirect
from shop.models import Products
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GalleryProducts, GalleryItem
from sellers.models import Shop
from collaborator.views import check_collab_and_jobs



def count_shop_gallery(shop_id):
    return GalleryProducts.objects.filter(shop__id = shop_id).count()



@login_required
def add_gallery(request,shop_id):
    shop = get_object_or_404(Shop,id = shop_id)

    if not check_collab_and_jobs(request, 'gallery_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)


    if request.method == 'POST':
        products = Products.objects.filter(id__in=request.POST.get('product_ids', []))

        if not products.exists():
            return render(
                request, 
                'gallery_products/add_gallery.html', 
                {
                    'error': 'محصولات وارد شده معتبر نیستند.',
                }
            )


        gallery_product = GalleryProducts.objects.create(shop=shop)
        gallery_product.product.set(products)
        gallery_product.save()
 
        for i in range(1, 100):  
            image = request.FILES.get(f'image_new_{i}')

            if image:
                GalleryItem.objects.create(
                    gallery_product=gallery_product,
                    image=image,
                )
        return redirect('gallery:list_product_gallery',shop_id)

    return render(
        request, 
        'gallery_products/add_gallery.html',
        {
            'products':Products.objects.filter(shop__id = shop_id)
        }
    )



def product_gallery(request,product_id):
    return render(
        request,
        'gallery_products/product_gallery.html',
        {
            'gallery_items':GalleryItem.objects.filter(gallery_product__product__id = product_id),
        }
    )



@login_required
def list_product_gallery(request,shop_id):
    galleries = GalleryProducts.objects.filter(shop__id=shop_id).prefetch_related('product', 'galleryitem_set')

    if not check_collab_and_jobs(request, 'gallery_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    return render(
        request, 
        'gallery_products/list_product_gallery.html', 
        {
            'galleries': galleries,
        }
    )



@login_required
def delete_gallery(request, gallery_id,shop_id):
    get_object_or_404(Shop,id = shop_id)
    gallery = get_object_or_404(GalleryProducts, id=gallery_id)

    if not check_collab_and_jobs(request, 'gallery_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
     
    
    GalleryItem.objects.filter(gallery_product=gallery).delete()
    gallery.delete()
    messages.success(
        request,
        'گالری با موفقیت حذف شد!'
    )
    return redirect('gallery:list_product_gallery',shop_id)
 


@login_required
def edit_gallery(request, gallery_id,shop_id):
    gallery = get_object_or_404(GalleryProducts, id=gallery_id)
    
    if not check_collab_and_jobs(request, 'gallery_permissions', shop_id):
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id) 
    

    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids', '')
        products = Products.objects.filter(id__in=product_ids)
        gallery.product.set(products)
 
        to_delete_ids = request.POST.getlist('delete_images')   
        if to_delete_ids:
            GalleryItem.objects.filter(id__in=to_delete_ids, gallery_product=gallery).delete()
 
        for item in gallery.galleryitem_set.all():
                item.save()
 
        i = 1
        while True: 
            image = request.FILES.get(f'image_new_{i}')
            if not image:
                break
 
            GalleryItem.objects.create(
                gallery_product=gallery,
                image=image,
            )
            i += 1
        return redirect('gallery:list_product_gallery',shop_id)

    else: 
        gallery_products = gallery.product.all()
        products = Products.objects.filter(shop__id=shop_id).exclude(id__in=gallery_products)
        return render(
            request,
            'gallery_products/edit_gallery.html', 
            {
                'gallery': gallery,
                'g_products':gallery_products,
                'products':products,
                'images': gallery.galleryitem_set.all(),
            }
        )
