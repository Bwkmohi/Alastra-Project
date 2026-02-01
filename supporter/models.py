from django.db import models
from accaunts.models import UserAuthentication,NationalIDAuthentication
from tiketing.models import ResponseToTiket

 

class Supporter(models.Model):
    user = models.ForeignKey(UserAuthentication, on_delete=models.CASCADE)
    nation_card = models.ForeignKey(NationalIDAuthentication,on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.user.username



class SupporterActivity(models.Model):
    supporter = models.ForeignKey(Supporter, on_delete=models.CASCADE)
    chat_views = models.ManyToManyField('ChatView', blank=True)
    messages = models.ManyToManyField('ChatMessages', blank=True)
    tickets = models.ManyToManyField(ResponseToTiket, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.supporter.user.user.username if self.supporter else "No Supporter"
    
    def counts(self, type):
        count = 0
        if type == 'messages':
            count = self.messages.count()

        elif type == 'chats':
            count = self.chat_views.count()

        elif type == 'tickets':
            count = self.tickets.count()
            
        return count
 

class ChatMessages(models.Model):   
    supporter = models.ForeignKey(Supporter, related_name='supporter', on_delete=models.CASCADE,null=True,blank=True)
    chat_view = models.ForeignKey('ChatView',on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    user_message = models.BooleanField(default=False)
    supporter_message = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    responsed = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=False)

    def __str__(self):
        return f"{self.content[:20]}"



class ChatView(models.Model):
    created = models.BooleanField(default=False)
    chat = models.ForeignKey(ChatMessages,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return str(self.pk)
    
    def make_true_messages(self):
        for i in ChatMessages.objects.filter(
            chat_view__id = self.pk
        ):
            i.responsed = True
            i.save()