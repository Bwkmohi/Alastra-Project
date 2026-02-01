from django.db import models
from django.contrib.auth.models import User
from shop.models import Products



class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    send_notification = models.BooleanField(default=False)
    alert_in_change_price = models.BooleanField(default=False)
    alert_price = models.FloatField(null=True,blank=True)
    direction = models.CharField(max_length=10, choices=(('above', 'بیشتر'), ('below', 'کمتر')),null=True,blank=True)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"