from django.db import models
from django.contrib.auth.models import User



class CategoryTiket(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

 

class Tikets(models.Model):   
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryTiket,on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    text = models.TextField()
    responsed = models.BooleanField(default=False)
    image = models.ImageField(max_length=1000,upload_to='media/tiket_image',blank=True,null=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name
    
    def text_(self):
        return self.text[:33] + ' ...'



class ResponseToTiket(models.Model):
    response_for_user = models.ForeignKey(Tikets,on_delete=models.CASCADE,related_name='responsed_tiket')
    response_text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.response_for_user.user.username