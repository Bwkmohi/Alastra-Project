from django.db import models
from django.contrib.auth.models import User


class UserFace(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_image = models.ImageField(upload_to='media/face_data',null=True,blank=True)
    password = models.CharField(max_length=200)
    auto_lock_time  = models.IntegerField(default=15)
    entred_password_at =  models.DateTimeField(auto_now_add=False,null=True,blank=True)
    is_entered = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}"