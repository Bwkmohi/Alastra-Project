from django.shortcuts import render,get_object_or_404 ,redirect
from django.contrib.auth.models import User
from sellers.models import Shop
from django.contrib import messages
from sellers.check import check_is_seller
from accaunts.models import UserAuthentication
from accaunts.check_auth import check_user,check_user_authentication
from .models import ShopCollaborator
from .models import CollaboratorActivity
from accaunts.models import NationalIDAuthentication


def count_shop_collaborators(shop_id):
    return ShopCollaborator.objects.filter(shop__id=shop_id).count()



def collaborator_add(request, shop_id):
    if check_collab_and_jobs(request, 'can_add_collaborators', shop_id) == False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)

    seller = check_is_seller(request)
    if not seller:
        return redirect('acc:authentication')

    if request.method == 'POST':
        username = request.POST.get('username')
        userid = request.POST.get('userid')
        data = request.POST.get
        shop = get_object_or_404(Shop, id=shop_id, seller=seller)

        try:
            user = User.objects.get(username=username, id=userid)
            if ShopCollaborator.objects.filter(shop=shop, user=user).exists():
                messages.warning(request, "این کاربر قبلاً به عنوان همکار ثبت شده است.")

            else:
                try:
                    user_authentication=UserAuthentication.objects.get(user=user)
                except UserAuthentication.DoesNotExist:
                    messages.warning(
                        request,
                        ''
                    )
                    return redirect()
                # try:
                #     national_id_auth=NationalIDAuthentication.objects.get(user=user)
                # except NationalIDAuthentication.DoesNotExist:
                #     messages.warning(
                #         request,
                #         ''
                #     )
                #     return redirect()
                
                c = ShopCollaborator.objects.create(
                    shop=get_object_or_404(Shop, id=shop_id, seller=seller),
                    user=user,
                    user_authentication=user_authentication,
                    # national_id_auth=national_id_auth,
                    can_add_product=bool(request.POST.get('can_add_product')),
                    can_delete_product=bool(data('can_delete_product')),
                    can_edit_product=bool(data('can_edit_product')),
                    can_response_questions=bool(data('can_response_questions')),
                    can_edit_coupon=bool(data('can_edit_coupon')),
                    can_add_coupon=bool(data('can_add_coupon')),
                    can_remove_coupon=bool(data('can_remove_coupon')),
                    can_edit_orders=bool(data('can_edit_orders')),
                    can_remove_comments=bool(data('can_remove_comments')),
                    can_see_products=bool(data('can_see_products')),
                    can_see_comments_and_questions=bool(data('can_see_comments_and_questions')),
                    can_see_coupons=bool(data('can_see_coupons')),
                    can_see_orders=bool(data('can_see_orders')),
                    can_edit_collaborators=bool(data('can_edit_collaborators')),    
                    can_see_collaborators=bool(data('can_see_collaborators')),
                    can_add_collaborators=bool(data('can_add_collaborators')),
                    can_remove_collaborators=bool(data('can_remove_collaborators')),
                    gallery_all_permissions=bool(data('gallery_all_permissions')),
                    story_all_permissions=bool(data('story_all_permissions')),
                    product_video_permissions=bool(data('product_video_permissions')),
                )

                if not check_collabrator(request, shop_id):pass
                else:create_activity(request, 'افزودن همکار ', c.pk, 'ADD', shop_id)
                messages.success(
                    request, 
                    f"همکار {user.username} با موفقیت اضافه شد."
                )
                return redirect('coll:collaborators_list', shop_id=shop_id)

        except User.DoesNotExist:
            messages.error(
                request, 
                "کاربری با این مشخصات یافت نشد."
            )
        return redirect('coll:collaborators_list', shop_id=shop_id)


    return render(
        request, 
        'collaborator/collaborator_add.html', 
        {
            'users': User.objects.all(),
            'shop': get_object_or_404(Shop, id=shop_id, seller=seller),
        }
    )



def collaborator_edit(request,shop_id,coll_id):
    collaborator = get_object_or_404(
        ShopCollaborator,id = coll_id
    )

    if check_collab_and_jobs(request,'can_edit_collaborators',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    if request.method == 'POST':
        data = request.POST.get

        collaborator.can_add_product=bool(data('can_add_product'))
        collaborator.can_delete_product=bool(data('can_delete_product'))
        collaborator.can_edit_product= bool(data('can_edit_product'))
        collaborator.can_response_questions=bool(data('can_response_questions'))
        collaborator.can_edit_coupon=bool(data('can_edit_coupon'))
        collaborator.can_add_coupon=bool(data('can_add_coupon'))
        collaborator.can_remove_coupon=bool(data('can_remove_coupon'))
        collaborator.can_edit_orders=bool(data('can_edit_orders'))
        collaborator.can_remove_comments=bool(data('can_remove_comments'))    
        collaborator.can_see_products=bool(data('can_see_products'))
        collaborator.can_see_comments_and_questions=bool(data('can_see_comments_and_questions'))
        collaborator.can_see_coupons=bool(data('can_see_coupons'))
        collaborator.can_see_orders=bool(data('can_see_orders'))
        collaborator.can_edit_collaborators=bool(data('can_edit_collaborators'))
        collaborator.can_see_collaborators=bool(data('can_see_collaborators'))
        collaborator.can_add_collaborators=bool(data('can_add_collaborators'))
        collaborator.can_remove_collaborators=bool(data('can_remove_collaborators'))
        collaborator.gallery_all_permissions=bool(data('gallery_all_permissions'))
        collaborator.story_all_permissions=bool(data('story_all_permissions'))
        collaborator.product_video_permissions=bool(data('product_video_permissions'))
        collaborator.active = bool(data('active'))

        collaborator.save()

        if not check_collabrator(request,shop_id):pass
        else:create_activity(request,'ویرایش همکار ',collaborator.pk,'EDIT',shop_id)

        messages.success(
            request,
            'همکار با موفقیت اپدیت شد!'
        )
        return redirect('coll:collaborators_list', shop_id=shop_id)

    return render(
        request,
        'collaborator/collaborator_edit.html',
        {
            'collaborator':get_object_or_404(ShopCollaborator,id=coll_id),
        }
    )



def collaborator_delete(request, coll_id, shop_id):
    collaborator = get_object_or_404(ShopCollaborator, id = coll_id, shop__id = shop_id)

    if check_collab_and_jobs(request, 'can_remove_collaborators', shop_id) == False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)

    
    if not check_collabrator(request, shop_id):pass
    else:
        create_activity(request, 'حذف همکار', collaborator.pk, 'REMOVE', shop_id)

    collaborator.delete()
    messages.success(
        request,
        'همکار با موفقیت حذف شد!'
    )
    return redirect('coll:collaborators_list', shop_id)



def collab_activity(request,collab_id,shop_id):
    if not check_user(request):
        return redirect('acc:login')
 
    if check_collab_and_jobs(request,'can_see_collab',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    return render(request,
        'collaborator/collab_activity.html',
        {
            'activity':CollaboratorActivity.objects.filter(
                shop=get_object_or_404(Shop,id=shop_id),
                shop_collaborator = get_object_or_404(ShopCollaborator,id=collab_id),
            )
        }              
    )



def collaborators_list(request, shop_id):
    if check_collab_and_jobs(request,'can_see_collaborators',shop_id)==False:
        messages.warning(
            request,
            'شما به این بخش دسترسی ندارید!'
        )
        return redirect('sellers:shop_dashbord',shop_id)
    
    return render(
        request, 
        'collaborator/collaborator_list.html',
          {
            'shop': get_object_or_404(Shop, id=shop_id),
            'collab': ShopCollaborator.objects.filter(shop__id=shop_id),
            'len': ShopCollaborator.objects.filter(shop=shop_id).count(),
            'shop_id':shop_id,
        }
    )



def create_activity(request,message,model_id,type,shop_id):
    CollaboratorActivity.objects.create(
        shop_collaborator = check_collabrator(request,shop_id),
        shop = get_object_or_404(Shop,id = shop_id),
        description = message,
        activity_id = model_id,
        activity_type = type
    )



def check_collabrator(request,shop_id):
    user=check_user(request)
    user_authentication=check_user_authentication(request)
    # national_id_auth=check_nation_cart(request)

    if not user:
        return None 
    
    if not user_authentication:
        return None
    
    # if not national_id_auth:
    #     return None
    # national_id_auth=national_id_auth,
    try:
        return ShopCollaborator.objects.get(
            user=user,active=True,user_authentication=user_authentication,
             shop__id = shop_id
        )
    except ShopCollaborator.DoesNotExist:
        return None



def collab_can_jobs(request, can, shop_id):
    collab = check_collabrator(request, shop_id)

    if not collab:
        return False

    permissions_map = {
        'product_add': collab.can_add_product,
        'product_delete': collab.can_delete_product,
        'product_edit': collab.can_edit_product,
        'response_questions': collab.can_response_questions,
        'coupon_edit': collab.can_edit_coupon,
        'coupon_add': collab.can_add_coupon,
        'coupon_remove': collab.can_remove_coupon,
        'edit_orders': collab.can_edit_orders,
        'can_see_orders': collab.can_see_orders,
        'can_see_products': collab.can_see_products,
        'see_messages': collab.can_see_comments_and_questions,
        'see_coupons': collab.can_see_coupons,
        'can_see_collaborators': collab.can_see_collaborators,
        'can_edit_collaborators': collab.can_edit_collaborators,
        'can_add_collaborators': collab.can_add_collaborators,
        'can_remove_collaborators': collab.can_remove_collaborators,
        'gallery_permissions': collab.gallery_all_permissions,
        'story_permissions': collab.story_all_permissions,
        'product_video_permissions':collab.product_video_permissions
    }
    return permissions_map.get(can, False)



def check_collab_and_jobs(request,job,shop_id):
    if check_collabrator(request,shop_id):
        return collab_can_jobs(request,f'{job}',shop_id)
    else:
        return check_is_seller(request)        