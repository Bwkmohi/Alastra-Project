from django.shortcuts import render,redirect,get_object_or_404
from tiketing.models import ResponseToTiket,Tikets,CategoryTiket
from django.contrib import messages
from supporter.views import check_supporter,get_or_create_supporter_activity,create_supporter_activity
from notifications.user_notification import notification_in_answered_ticket


def list_tikets(request):
    response_statuse = request.GET.get('filter_response_statuse')
    tikets = Tikets.objects.filter(responsed=False)

    if not check_supporter(request):
        return redirect('index')
    
    if response_statuse:
        pass

    return render(
        request,
        'response_tikets/list_tikets.html',
        {
            'tikets': tikets,
            'len':tikets.count(),
            'category':CategoryTiket.objects.all()
        }
    )



def filter_tikets(request,category_id):

    if not check_supporter(request):
        return redirect('index')

    category=get_object_or_404(CategoryTiket,id = category_id)
    tiket=Tikets.objects.filter(
        responsed = False,category = category
    )   

    return render(
        request,
        'response_tikets/list_tikets.html',
        {
            'filtered_category':category,
            'category':CategoryTiket.objects.all(),
            'tikets':tiket,
            'text':f'تیکت های پاسخ داده نشده | نتایج دسته بندی {category.title}   | پیدا شده ({tiket.count()})'
        }
    )



def response_to_tiket(request):

    if not check_supporter(request):
        return redirect('index')
    

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        text = request.POST.get('response_text')

        if not text:
            messages.error(
                request,
                'فیلد نمیتواند خالی باشد.!'
            )
            return redirect('list_tikets')
        
        tiket = get_object_or_404(Tikets, id=ticket_id)

        response=ResponseToTiket.objects.create(
            response_for_user=tiket,
            response_text=text,
        )

        tiket.responsed = True
        tiket.save()

        notification_in_answered_ticket(tiket.pk)
        get_or_create_supporter_activity(check_supporter(request))
        create_supporter_activity(
            request,
            type='tikets',object=response,supp=check_supporter(request)
        )
        messages.success(
            request,
            'تیکت پاسخ داده شد!'
        )
        return redirect('list_tikets') 