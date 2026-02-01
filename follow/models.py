from django.db import models
from sellers.models import Shop
from django.contrib.auth.models import User

class FolloweUnFollow(models.Model):
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username