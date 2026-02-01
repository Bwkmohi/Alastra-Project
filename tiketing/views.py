from django.shortcuts import render,redirect,get_object_or_404
from accaunts.check_auth import check_user
from tiketing.models import Tikets,CategoryTiket
from django.contrib import messages
import bleach

def send_tiket(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')


    if request.method == 'POST':

        title = request.POST.get('title')
        text = bleach.clean(request.POST.get('text'))
        image = request.FILES.get('image')
        category_=CategoryTiket.objects.get(id=request.POST.get('category'))

        Tikets.objects.create(
            user=user, category=category_, title=title, text=text, image=image
        )

        messages.success(
            request,
            'تیکت با موفقیت ثبت شد، بزودی پاسخ داده می‌شود.'
        )
        return redirect('mess:list_my_tikets')


    context = {
        'category':CategoryTiket.objects.all()
    }
    return render(
        request, 
        'tiketing/send_tiket.html',
        context
    )



def list_my_tikets(request):
    user = check_user(request)
    filter_value = request.GET.get('filter_tiket')

    if not user:
        return redirect('acc:login')
    
    
    if filter_value:
        if filter_value == 'responsed':
            tikets = Tikets.objects.filter(
                user = user,
                responsed = True 
            )
            
        elif filter_value == 'not_responsed':
            tikets = Tikets.objects.filter(
                user = user,
                responsed = False 
            )
            
        return render(
            request,
            'tiketing/list_my_tikets.html',
            {
                'tikets':tikets,
                'len':Tikets.objects.filter(user=user).count()
            }
        )
   
    return render(
        request,
        'tiketing/list_my_tikets.html',
        {
            'tikets':Tikets.objects.filter(user=user),
            'len':Tikets.objects.filter(user=user).count(),        
        }
    )



def edit_tiket(request, id):
    user = check_user(request)

    if not user:
        messages.warning(
            request,
            'لطفا وارد حساب خود شوید '
        )
        return redirect('acc:login')


    if request.method == 'POST':

        tiket = Tikets.objects.get(id=request.POST.get('id'))

        category = request.POST.get('category')
        category_ = CategoryTiket.objects.get(id=category)

        if tiket.responsed == True:
            messages.warning(
                request,''
            )
            return redirect()
        
        tiket.title = request.POST.get('title')
        tiket.category = category_
        tiket.text = bleach.clean(request.POST.get('text'))
        tiket.image = request.FILES.get('image')
        tiket.save()

        messages.success(
            request,
            'تیکت با موفقیت ثبت شد، بزودی پاسخ داده می‌شود.'
        )
        return redirect('mess:list_my_tikets')


    else:
        try:
            return render(
                request,
                'tiketing/edit_tiket.html',
                {
                    'tiket': Tikets.objects.get(user=user,id=id,responsed=False),
                    'category':CategoryTiket.objects.all()
                }
            )
        except Tikets.DoesNotExist:
            messages.error(
                request,
                'این تیکت قابل ویرایش نیست!'
            )
            return redirect('mess:list_my_tikets')



def remove_tiket(request,id):
    user = check_user(request)

    if not user:return redirect('acc:login')
        
    get_object_or_404(Tikets,id = id,user = user).delete()
    return redirect('mess:list_my_tikets')