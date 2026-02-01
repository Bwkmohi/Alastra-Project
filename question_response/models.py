from django.db import models
from django.contrib.auth.models import User
from shop.models import Products

 

class Question(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    text = models.TextField(max_length=120,null=True,blank=True)
    responsed = models.BooleanField(default=False)
    show_name = models.BooleanField(default=True)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

    def text_(self):
        return self.text[:30]



class Response(models.Model):
   seller = models.ForeignKey('sellers.Seller',on_delete=models.CASCADE)
   reply_ques = models.ForeignKey(Question,on_delete=models.CASCADE)
   response_text = models.TextField(max_length=120)
   time = models.DateTimeField(auto_now_add=True)

   def __str__(self):
        return self.seller.user.username

   def text_(self):
       return self.response_text[:105]