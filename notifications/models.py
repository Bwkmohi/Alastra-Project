from django.db import models
from django.contrib.auth.models import User

NOTIFICATION_FOR = [
    ('seller','seller'),
    ('user_authentication','user_authentication'),
    ('nation_id_cart','nation_id_cart'),
    ('public','public'),
    ('shop','shop'),
]

NOTIFICATION_TYPE = [
    ('private','private'),
    ('public','public'),
] 


class Svg(models.Model):
    svg_d = models.TextField()
    bg_color = models.CharField(max_length=300,default='bg-[#ffff]-50')
    svg_color = models.CharField(max_length=300,default='text-[#0bffffcc]-200')

    def __str__(self):
        return self.svg_d


class Notification(models.Model):
    subject = models.CharField(max_length=50)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    notification_type = models.CharField(max_length=100,choices=NOTIFICATION_TYPE,null=True,blank=True,default='public')
    notification_for = models.CharField(max_length=50,choices=NOTIFICATION_FOR,null=True,blank=True)
    svg = models.ForeignKey(Svg,on_delete=models.CASCADE,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
 
class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification = models.ForeignKey(Notification,on_delete=models.CASCADE,null=True,blank=True)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    added = models.BooleanField(default=False) 
    created = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return self.user.username

    def count_unseen_notifications(self):
        return UserNotification.objects.filter(
            user = self.user,
            is_read = False 
        ).count()
        

class UserNotificationsSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sent_notify_to_email = models.BooleanField(default=True)
    sent_notify_to_site = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.username