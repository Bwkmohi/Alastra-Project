from django.shortcuts import render,redirect,get_object_or_404
from accaunts.check_auth import check_user
from django.contrib import messages
from .models import CompareModel
from shop.models import Products
from smartgtp.views import get_exemple_products
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from shop.models import Products,ProductKeyValues,Comments



@csrf_exempt
def add_to_compare_by_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({
        'status': 'error'
        })
    if request.method == "POST":

        data = json.loads(request.body)
        product_ids = data.get('product_ids', [])

        for id in product_ids:
            CompareModel.objects.create(
                user = request.user,
                product = get_object_or_404(Products,id=id)
            )

        return JsonResponse({
            'status': 'success', 'action': 'cart', 'ids': product_ids
        })
    return JsonResponse({
        'status': 'error'
    })



def compare_view(request):
    user = check_user(request)
    compare = CompareModel.objects.filter(user=user)
    compare_list = get_product_dic(compare)


    if not user:
        return redirect('acc:login')

    return render(
        request,
        'compare/compare.html',
        {
            'compare': compare_list,
            'len': compare.count(),
        }
    )



def get_product_dic(compare):
    products_list = []
    for pr in compare:
        product_obj = pr.product
        key_values = ProductKeyValues.objects.filter(product=product_obj)

        details = []
        for kv in key_values:
            if kv.key and kv.value.strip():
                details.append({
                    'key': kv.key.key,
                    'value': kv.value.strip()
                })
            else:
                details.append({
                    'key': '-',
                    'value': '-'
                })

        rating = Comments.objects.filter(product=product_obj).first()
        dic = {
            'id': product_obj.pk,
            'compare_id': pr.pk,
            'name': product_obj.name,
            'image': product_obj.image.url if product_obj.image else None,
            'price': product_obj.price_(),
            'description':product_obj.description_(),
            'brand': str(product_obj.brand) if product_obj.brand else '-',
            'color': str(product_obj.color) if product_obj.color else '-',
            'rating': rating.total_rates() if rating else 0,
            'details': details,
        }
        products_list.append(dic)
    return products_list

 



def add_product_to_compare(request, product_id):
    user = check_user(request)
    product = get_object_or_404(Products, id=product_id)

    if not user:
        return redirect('acc:login') 
    
    if not CompareModel.objects.filter(user = user,product = product).exists():
        CompareModel.objects.create(user=user, product=product)
        messages.success(
            request, 
            f" محصول به لیست مقایسه اضافه شد!"
        )
        return redirect('com:compare_view')
    else:
        messages.warning(
            request,
            f"محصول از قبل  در لیست وجود دارد!"
        )
        return redirect('com:compare_view')



def remove_from_compare(request,id):
    
    user = check_user(request)
    if not user:return redirect('acc:login')
        
    get_object_or_404(CompareModel,id = id).delete()
    messages.success(
        request,
        'محصول از لیست مقایسه حذف شد!'
    )
    return redirect('com:compare_view')
