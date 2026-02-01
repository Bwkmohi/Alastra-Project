from django.shortcuts import get_object_or_404,redirect
from accaunts.check_auth import check_user
from .models import Question
from shop.models import Products
from django.contrib import messages
from notifications.shop_notification import notification_in_new_question
import bleach


def add_product_question(request,id):
    user = check_user(request)
    
    if not user:
        messages.warning(
            request,
            'لطفا وارد حساب خود شوید '
        )
        return redirect('acc:login')
    
    product=get_object_or_404(
        Products,id = id
    )

    if request.method == 'POST':
        url = request.POST.get('url')
        show_name = bool(request.POST.get('show_name'))

        question=Question.objects.create(
            user = user,
            product = product,
            text = bleach.clean(request.POST.get('text')),
            show_name = show_name
        )

        notification_in_new_question(question.pk)
        messages.success(
            request,
            'سوال با موفقیت افزوده شد! به زودی پاسخ داده خواهد شد!'
        )
        if not url:return redirect('product_detail', id=product.pk, slug=product.slug)
        else:return redirect(url)

    else:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound()

