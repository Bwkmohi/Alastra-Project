
from django.db import models
from django.contrib.auth.models import User
from shop.models import Products


class CompareModel(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username