from .models import ChatHome
from .models import BlackList
from django.shortcuts import get_object_or_404
from .models import ChatHome

def check_chathome(request,sender,receiver,chat_home_id):
    chat_home = get_object_or_404(ChatHome,id = chat_home_id)
    if chat_home.sender_ch == sender or chat_home.sender_ch == receiver or chat_home.receiver_ch == receiver or chat_home.receiver_ch == sender:
        return chat_home
    else:return None
        

 
def check_black_list(sender, receiver):
    if BlackList.objects.filter(user=receiver, blocked_user=sender).exists():return True
    elif BlackList.objects.filter(user=sender, blocked_user=receiver).exists():return True
    else:return False