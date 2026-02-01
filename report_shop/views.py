from django.shortcuts import render,get_object_or_404,redirect
from .models import ReportCategory,ReportShop
from sellers.models import Shop
from accaunts.check_auth import check_user
from django.contrib import messages
import bleach


def report_add(request,shop_id):
    user=check_user(request)
    shop = get_object_or_404(Shop,id = shop_id)

    if not user:
        return redirect('acc:login')
    
    if request.method == 'POST':
        report_category = get_object_or_404(ReportCategory,id = request.POST.get('category_id'))

        if ReportShop.objects.filter(user = user,shop = shop,category = report_category).exists():
            messages.warning(
                request,
                'این گزارش قبلا ثبت شده است. نمیتوانید دوباره گزارش ثبت کنید'
            )
            return redirect('acc:pro')
        
        ReportShop.objects.create(user = user,shop = shop,category = report_category,text = bleach.clean(request.POST.get('text')))
        messages.success(
            request,
            'گرازش با موفقیت ثبت شد به زودی برسی خواهد شد!'
        )
        return redirect('acc:pro')

    return render(
        request,
        'report_shop/report_add.html',
        {
            'category':ReportCategory.objects.all(),   
        }
    )



def reports_list(request):
    if request.user.is_superuser:
        return render(
            request,
            'report_shop/reports_list.html',
            {
                'reports':ReportShop.objects.filter(is_checked=False),
                'len':ReportShop.objects.filter(is_checked=False).count()
            }
        )
    return redirect('index')



def report_detail(request,id):
    report=get_object_or_404(
        ReportShop,
        id=id,
    ) 

    if request.method=='POST':
        report.is_true = bool(request.POST.get('is_true'))
        report.is_checked = bool(request.POST.get('is_checked'))
        report.save()

        messages.success(
            request,
            'گرازش برسی شد!'
        )
        return redirect('rep:reports_list')
    
    return render(
        request,
        'report_shop/report_detail.html',
        {
            'report':report
        }   
    ) 