from django.db import models
from django.contrib.auth.models import User
from reservations.models import ProvinceCategory,Citys

GENDER = [
    ('MEN','MEN'),
    ('WOMEN','WOMEN'),
]
 
class UserAuthentication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ImageField(upload_to='media/user_profile', null=True, blank=True)
    phone = models.CharField(max_length=11)
    national_code = models.IntegerField()
    address = models.CharField(max_length=500)
    province = models.ForeignKey(ProvinceCategory, on_delete=models.CASCADE)
    city = models.ForeignKey(Citys,on_delete=models.CASCADE)
    gender = models.CharField(max_length=30,choices=GENDER,null=True,blank=True)
    age = models.DateField() #تاریخ تولد
    postal_code = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
         

class NationalIDAuthentication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_authentication = models.ForeignKey(UserAuthentication, on_delete=models.CASCADE,null=True,blank=True)
    national_id_image = models.ImageField(upload_to='media/national_id_images')
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} - National ID Auth'