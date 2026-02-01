from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from shop.models import Products
 
 
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    product = models.ForeignKey(Products,on_delete=models.CASCADE,null=True,blank=True)
    image = models.ImageField(upload_to='media/chat_image', blank=True, null=True)
    seen = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    timestamp = models.DateTimeField(auto_now_add=True)
    chat_home = models.ForeignKey('ChatHome',on_delete=models.CASCADE,null=True,blank=True,related_name='messages_home')

    def __str__(self):
        return f"{self.sender} to {self.receiver}: {self.content[:20]}"


class ChatHome(models.Model):
    sender_ch = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='sender_ch')
    receiver_ch =  models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    messages = models.ForeignKey(Message,on_delete=models.CASCADE,related_name='chat_home_messages',null=True,blank=True)
    fav = models.BooleanField(default=False)

    def __str__(self):
        return f'{str(self.pk)}'
    
    def get_Messages(self):
        return Message.objects.filter(
                chat_home = ChatHome(self)
            ).order_by('timestamp')
    
    def get_last_message(self):
        message_model = Message.objects.filter(
            Q(sender=self.sender_ch, receiver=self.receiver_ch) | Q(sender=self.receiver_ch, receiver=self.sender_ch)
        ).order_by('-timestamp').first()
        if not message_model:
            return {
                'message':'...',
                'timestamp':''
            }
        return {
            'message':message_model.content[:20] if message_model.content else '...',
            'timestamp':message_model.timestamp if message_model.timestamp else ''
        }
    

class BlackList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    blocked_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='blocked_user')

    def __str__(self):
        return self.user.username