from django.http import JsonResponse
from .models import ChatHome,Message
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q, F,CharField, Case, When
from shop.models import Products
from accaunts.check_auth import check_user
from django.shortcuts import redirect



def chat_homes_view(user):
    return ChatHome.objects.filter(Q(sender_ch=user) | Q(receiver_ch=user)).order_by('-messages__timestamp').distinct()
 

#  لیست اشتراک گذاری محصولات با کاربران
def shareable_list(request):
    user = request.user
    if not user.is_authenticated:
        return None
    
    if user:
        chats = ChatHome.objects.filter(Q(sender_ch__id=user.pk) | Q(receiver_ch__id=user.pk))

        return chats.annotate(
            opponent_username=Case(
                When(sender_ch__id=user.pk, then=F('receiver_ch__username')),
                When(receiver_ch=user, then=F('sender_ch__username')),
                output_field=CharField(),
            ),
            opponent_first_name=Case(
                When(sender_ch__id=user.pk, then=F('receiver_ch__first_name')),
                When(receiver_ch=user, then=F('sender_ch__first_name')),
                output_field=CharField(),
            ),
            opponent_last_name=Case(
                When(sender_ch__id=user.pk, then=F('receiver_ch__last_name')),
                When(sender_ch__id=user.pk, then=F('sender_ch__last_name')),
                output_field=CharField(),
            )
        ).values('id', 'opponent_username', 'opponent_first_name', 'opponent_last_name')

        

#    دریافت محصولات برای ارسال به چت
@csrf_exempt  
def send_selected_products(request):
    user = check_user(request)

    if not user:
        return redirect('acc:login')

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("product_ids", [])
            chat_home_id = data.get("chat_home_id")

            if not chat_home_id or not product_ids:
                return JsonResponse({"error": "chat_home_id و product_ids باید ارسال شوند."}, status=400)

            try:
                chat_home = ChatHome.objects.get(id=chat_home_id)
            except ChatHome.DoesNotExist:
                return JsonResponse({"error": "چت مورد نظر یافت نشد."}, status=404)

            products = Products.objects.filter(id__in=product_ids)
            if chat_home.receiver_ch == user.pk:rec = chat_home.sender_ch
            else:rec = chat_home.receiver_ch

            for product in products:
                Message.objects.create(
                    sender = request.user,
                    receiver = rec,
                    product = product,
                    chat_home = chat_home
                )

            return JsonResponse({
                "status": "success",
                "message": "محصولات با موفقیت ارسال شدند.",
                "product_ids": product_ids,
                "chat_home_id": chat_home_id
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "داده‌های JSON نامعتبر است."}, status=400)

    return JsonResponse({"error": "متد درخواست غیرمجاز است."}, status=405)