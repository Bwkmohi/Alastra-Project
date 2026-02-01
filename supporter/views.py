from django.shortcuts import render,get_object_or_404,redirect
from .models import ChatView,ChatMessages,Supporter,SupporterActivity
from django.http import JsonResponse
from django.contrib import messages
from accaunts.check_auth import check_user_authentication,check_user
from .sessions import save_chat_view_id_in_session
from django.utils import timezone
from tiketing.models import ResponseToTiket 
import datetime 


def check_supporter(request):
    
    if not check_user(request):return None
    
    if not check_user_authentication(request):return None

    try:
        return Supporter.objects.get(user = check_user_authentication(request),active = True)
    except Supporter.DoesNotExist:
        return None



def get_or_create_chat_view(request):
    session = request.session.get('suppoerterchat',{})

    if check_supporter(request):
        return 'is_supporter'

    try:
        if session:
            for session_id in session:
                return ChatView.objects.get(id=session_id)            
        else:
            chat_view = ChatView.objects.create(created=True)
            save_chat_view_id_in_session(request, chat_view.pk)
    except ChatView.DoesNotExist:
        chat_view = ChatView.objects.create(created=True)
        save_chat_view_id_in_session(request, chat_view.pk)

    return chat_view



def chat(request):
    chat_view = get_or_create_chat_view(request)


    if chat_view == 'is_supporter':
        return redirect('supp:list_questions')

    return render(
        request,
        'supporter/user_chat_view.html',
        {
            'ch_id': chat_view.pk
        }
    )


 
def response_page(request, chat_id):
    supporter = check_supporter(request)


    if not supporter:
        messages.error(
            request,
            'شما به این صفحه دسترسی ندارید!'
        )
        return redirect('index')
    
    
    get_or_create_supporter_activity(supporter)


    try:
        chat_view = ChatView.objects.get(id=chat_id)
        chat_messages = ChatMessages.objects.filter(
            chat_view__id=chat_id
        )

        return render(
            request,
            'supporter/user_chat_view.html',
            {
                'message': chat_messages.distinct(),
                'ch_id': chat_view.pk
            }
        )
    
    except ChatView.DoesNotExist:
        messages.error(
            request,
            'چنین گفتگویی وجود ندارد! یا توسط کاربر حذف شده است'
        )
        return redirect('supp:list_questions')



def send_message(request):
    supporter = check_supporter(request)
    chat_view = get_object_or_404(ChatView, id=request.POST.get('ch_id'))
    content = request.POST.get('content')


    if supporter:

        msg = ChatMessages.objects.create(
            supporter = supporter,
            chat_view=chat_view,
            content=content,
            responsed=True,
            supporter_message=True,
            user_message=False,
            created = datetime.datetime.now()
        )
        ChatMessages.objects.filter(chat_view=chat_view).update(responsed=True)

        get_or_create_supporter_activity(supporter)
        create_supporter_activity(request, 'message', msg, supporter)
        create_supporter_activity(request,'chat_views',chat_view.pk,supporter)

    else:

        msg = ChatMessages.objects.create(
            chat_view=chat_view,
            content=content,
            user_message=True,
            supporter_message=False,
            created = datetime.datetime.now()
        )
 
    return JsonResponse({
        'data':'data'
    })



def fetch_unseen_messages(request, chat_id):

    chat_view = get_object_or_404(ChatView, id=chat_id)
    messages = ChatMessages.objects.filter(chat_view=chat_view).order_by('id')


    data = [{
        'id': msg.pk,
        'content': msg.content,
        'user_message': msg.user_message,
        'supporter_message': msg.supporter_message,
        'created': msg.created.isoformat() if msg.created else None,
    } for msg in messages]


    return JsonResponse({
        'messages': data
    })



def list_questions(request):
    list_chats = []
    supporter = check_supporter(request)

    if not supporter:
        return redirect('index')

    for i in ChatMessages.objects.filter(responsed = False,user_message = True):
        if i.chat_view.pk  not in list_chats:
            list_chats.append(i.chat_view.pk)

    return render(
        request,
        'supporter/list_questios.html',
        {
            'unread_chats':ChatMessages.objects.filter(
                chat_view__id__in=list_chats
            ).distinct(),
        }
    )



def dashbord_supporter(request):
    
    supporter = check_supporter(request)

    if not supporter:
        return redirect('acc:pro')
    supporter_activity = SupporterActivity.objects.filter(supporter=supporter).first()
    

    list_Respondes = []
    list_Chats = []
    for i in SupporterActivity.objects.filter(supporter=supporter):
        for rt in i.tickets.all().order_by('-time')[:5]:
            list_Respondes.append(rt.pk)

        for ch in i.chat_views.all().order_by('-created')[:5]:
            list_Chats.append(ch.pk)
    
    today = timezone.now().date()
    today_activity = SupporterActivity.objects.filter(
        supporter=supporter,
        time__date=today
    ).count()

    

    context = {
        'supporter': supporter,
        'supporter_activity': supporter_activity,
        'last_tickets':ResponseToTiket.objects.filter(id__in=list_Respondes),
        'last_chats': ChatView.objects.filter(id__in=list_Chats),
        'today_activity': today_activity,
        'count_messages':supporter_activity.counts(type='messages') if supporter_activity else 0,
        'chats':supporter_activity.counts(type='chats') if supporter_activity else 0,
        'response_tickets':supporter_activity.counts(type='tickets') if supporter_activity else 0,
    }
    
    return render(request, 'supporter/supporter_dashbord.html', context)


def get_or_create_supporter_activity(supp):
    try:
        return SupporterActivity.objects.get(
            supporter = supp,
        )
    except SupporterActivity.DoesNotExist:
        return SupporterActivity.objects.create(
            supporter = supp,
        )



def create_supporter_activity(request,type,object,supp):
    
    if type == f'{type}':
        supporter=SupporterActivity.objects.get(
            supporter = supp
        )
 
        if type == 'chat_views':
            supporter.chat_views.add(
                object
            )

        elif type == 'message':
            supporter.messages.add(
                object
            )

        elif type== 'tikets':
            supporter.tickets.add(
                object
            )
