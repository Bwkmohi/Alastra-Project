from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Message,ChatHome
from accaunts.check_auth import check_user,check_user_authentication
from .check import check_black_list,check_chathome
from .models import BlackList
from notifications.user_notification import you_have_new_message
from accaunts.models import UserAuthentication



def list_chathomes(request):
    list_chathomes_id = []
    list_chathomes_ = []
    user = check_user(request)
    auth_user = check_user_authentication(request)

    if not user:
        return redirect('acc:login')
    
    if not auth_user:
        return redirect('acc:authentication')
    
    for i in ChatHome.objects.filter(Q(sender_ch=user) | Q(receiver_ch=user)).order_by('-messages__timestamp').distinct():
        if user.pk == i.sender_ch.pk:   rec = i.receiver_ch
        else:    rec = i.sender_ch

        if check_black_list(user,rec) == False:
            list_chathomes_id.append(i.pk)

    chathomes = ChatHome.objects.filter(id__in=list_chathomes_id)

    postValue = request.GET.get('filter')
    if postValue == 'fav':
        chats=chathomes.filter(
            fav=True
        )    

    for i in chats if postValue == 'fav' else chathomes:
        try:
            if request.user.pk == i.receiver_ch:
                user_authentication=UserAuthentication.objects.get(user=i.sender_ch)
            else:
                user_authentication=UserAuthentication.objects.get(user=i.receiver_ch)
        except user_authentication:
            pass
        
        
        if user_authentication.profile:image = user_authentication.profile.url
        else:image = ''

        list_chathomes_.append(
            {
                'sender_ch':i.sender_ch,
                'receiver_ch':i.receiver_ch,
                'profile_image_url':image,
                'last_message':i.get_last_message(),
                'id':i.pk,
                'pk':i.pk
            }
        )

    return render(
        request,
        'chat/list_chathomes.html',
        {
            'chathomes':list_chathomes_,
            'blocked_users':BlackList.objects.filter(user=request.user)
        }
    )

#   صفحه چت بین دو کاربر
def chat_home(request, receiver_id, chat_home_id):

    user = check_user(request)
    rec_profile = get_object_or_404(UserAuthentication,user__id = receiver_id).profile
    sender_profile = get_object_or_404(UserAuthentication,user__id = user.pk).profile
    receiver = get_object_or_404(User, id=receiver_id)
    chat_home = get_object_or_404(ChatHome, pk=chat_home_id)
    messages_qs = Message.objects.filter(chat_home__id=chat_home.pk)
    messages_qs.update(seen=True)

    if not user:
        return redirect('acc:login')
    
    if user == receiver:
        messages.error(
            request, 
            'نمیتوانید به خودتان پیام ارسال کنید.'
        )
        return redirect('acc:pro')
 
    if check_black_list(user,receiver) == True:
        messages.warning(
            request,
            'شما مسدود شدید! نمیتوانید پیام ارسال کنید!'
        )
        return redirect('list_chathomes')

    if not check_chathome(request,sender=request.user, chat_home_id=chat_home_id, receiver=receiver):
        messages.error(
            request,
            'این صفحه به شما تعلق ندارد. '
        )
        return redirect('acc:pro')

    return render(
        request,
        'chat/list_messages.html',
        {
            'receiver_profile':rec_profile if rec_profile else '',
            'sender_profile':sender_profile if sender_profile else '',
            'receiver_id': receiver_id,
            'messages': messages_qs,
            'receiver': receiver,
            'ch_id': chat_home.pk,
            'chat_home': chat_home,
        }
    )

# طوری بساز که مستقیم بشه چت باخت مثل ارسال پیام به فروشنده
def new_chat(request):
    user = check_user(request)
    if not user:
        messages.error(
            request, 
            'شما باید اول به حساب خود وارد شوید'
        )
        return redirect('acc:login')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        user_id = request.POST.get('user_id')
        try:
            if user_id:
                receiver = User.objects.get(username = username,id=user_id)
            else:
                receiver = User.objects.get(username = username)
            
            if not UserAuthentication.objects.filter(user=receiver).exists():
                messages.warning(
                    request,
                    'نمیتوانید به کاربر اهراز هوبت نشده پیام ارسال کنید!'
                )
                # if not url:
                return redirect('list_chathomes')
                # else:
            
            else:
                chathome = get_or_create_chathome(request,user,receiver)
                if not user.pk == receiver.pk:
                    if not chat_home:
                        ch=ChatHome.objects.create(sender_ch = user,receiver_ch = receiver
                        )
                        return redirect('chat',receiver.pk,ch.pk)   
                    else:
                        messages.warning(
                            request,
                            'چنین گفتگویی از قبل وجود دارد'
                        )
                        return redirect('chat',receiver.pk,chathome.pk)   
                else:
                    messages.error(
                        request,
                        'نمیتوانید به خودتان پیام ارسال کنید!'
                    )
                    return redirect('list_chathomes')
                
        except User.DoesNotExist:
            messages.error(
                request,
                'چنین کاربری یافت نشد!'
            )
            return redirect('list_chathomes')

import bleach
@require_POST
def send_message(request):
    user = check_user(request)
    receiver = get_object_or_404(User, id=request.POST.get('receiver'))
    chat_home = get_or_create_chathome(request, user, receiver)
    reply_to_id = request.POST.get('reply_to')
    image = request.FILES.get('image')

    cleaned_message = bleach.clean(request.POST.get('content'))

    if not user:
        messages.error(
            request, 
            'شما باید اول به حساب خود وارد شوید'
        )
        return redirect('acc:login')

    if check_black_list(sender=user, receiver=receiver):
        return JsonResponse({'data': 'نمیتوانید پیام ارسال کنید!'})

    reply_to = None
    if reply_to_id:
        try:
            reply_to = Message.objects.get(id=reply_to_id)
        except Message.DoesNotExist:
            reply_to = None

    msg = Message.objects.create(
        sender=user,
        receiver=receiver,
        content=cleaned_message,
        reply_to=reply_to,
        timestamp=timezone.now(),
        chat_home=chat_home
    )

    if image:
        msg.image.save(image.name, image)
    msg.save()

    #  بدون نت ارور میده!
    you_have_new_message(msg.pk)
    return JsonResponse({'status':'success'})

 
def messages_list(request, ch_id):
    messages_data = []
    
    # دریافت پیام‌های جدید
    unseen_msgs = Message.objects.filter(chat_home__id=ch_id).order_by('timestamp')

    for msg in unseen_msgs:
        product_data = None  # ابتدا برای هر پیام محصول را برابر None قرار می‌دهیم
        
        if msg.product:
            product_data = {
                'id': msg.product.id,
                'slug': msg.product.slug,
                'url': f'/product/{msg.product.pk}/{msg.product.slug}/',
                'name': msg.product.name,
                'price': msg.product.price,
                'image': msg.product.image.url if msg.product.image else ''
            }

        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.pk,
            'content': msg.content,
            'image_url': msg.image.url if msg.image else '',
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'reply_to_id': msg.reply_to.id if msg.reply_to else None,
            'reply_to_content': msg.reply_to.content if msg.reply_to else '',
            'product': product_data  # ارسال محصول برای هر پیام به صورت جداگانه
        })

    return JsonResponse({
        'messages': messages_data
    })


def add_to_black_list(request,id):
    user = check_user(request)
    block_user = get_object_or_404(User,id = id)

    if not user:
        return redirect('acc:login')
    
    if BlackList.objects.filter(blocked_user = block_user).exists():
        messages.error(
            request,
            'این کاربر قبلا به لیست مسدود شده ها اضافه شده!'
        )

    BlackList.objects.create(user = user,blocked_user = block_user)

    messages.success(
        request,
        f'کاربر {block_user.username} به لیست مسدود شدگان افزوده شد'
    )
    return redirect('list_chathomes')


def remove_from_black_list(request,id):
    user = check_user(request)
    black_list = get_object_or_404(BlackList,id = id)

    if not user:
        return redirect('acc:login')
    
    black_list.delete()

    messages.success(
        request,
        'از لیست سیاه خارج شد!'
    )
    return redirect('list_chathomes')
    
    
def delete_chat_home(request,id):
    chat_home=get_object_or_404(ChatHome,id = id)
    chat_home.delete()

    messages.success(
        request,
        'گفتگوی شما با موفقیت حذف شد! '
    )
    return redirect('list_chathomes')


def add_to_favorites(request,id):

    chat=get_object_or_404(ChatHome,id = id)
    chat.fav = True
    chat.save()

    messages.success(
        request,
        'کاربر با موفقیت به موارد مورد علاقه اضافه شد!'
    )
    return redirect('list_chathomes')


def remove_from_favorites(request,id):
    chat = get_object_or_404(ChatHome,id = id)
    chat.fav = False
    chat.save()

    messages.success(
        request,
        'کاربر از موارد علاقه ها برداشته شد!'
    )
    return redirect('list_chathomes')


def get_or_create_chathome(request,sender,receiver):
    try:
        return ChatHome.objects.get(sender_ch = sender,receiver_ch = receiver)
    except ChatHome.DoesNotExist:
        try:
            return ChatHome.objects.get(sender_ch = receiver ,receiver_ch = sender)
        except ChatHome.DoesNotExist:
            return ChatHome.objects.create(sender_ch = sender,receiver_ch = receiver)


@require_POST
def delete_message(request):
    user = request.user

    try:
        msg = Message.objects.get(id=request.POST.get('message_id'))
    except Message.DoesNotExist:
        return JsonResponse({'error': 'پیام پیدا نشد'}, status=404)

    if msg.sender != user and msg.receiver != user:
        return JsonResponse({'error': 'دسترسی غیرمجاز'}, status=403)

    msg.delete()
    return JsonResponse(
        {
            'success': True
        }
    )