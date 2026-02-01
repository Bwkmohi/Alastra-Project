from django.db import models
from django.contrib.auth.models import User
from sellers.models import Shop



class ReportCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
 

class ReportShop(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE)
    category = models.ForeignKey(ReportCategory,on_delete=models.CASCADE)
    text = models.TextField(max_length=1099)
    is_checked = models.BooleanField(default=False)
    is_true = models.BooleanField(default=False)
    time =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username     