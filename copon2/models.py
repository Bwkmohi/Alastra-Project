from django.db import models
from shop.models import MainCategory
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_percent = models.BooleanField(default=True,verbose_name='number or %')
    value = models.PositiveIntegerField(validators=[MinValueValidator(1)],verbose_name='200$ or 20%')
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True,verbose_name='limit for use')  # اگر خالی باشه، محدودیتی نداره
    used_count = models.PositiveIntegerField(default=0)
    for_followers = models.BooleanField(default=False,blank=True,null= True)
    category = models.ForeignKey(MainCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name='coupons_for_categorys')
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    shop = models.ForeignKey('sellers.Shop',on_delete=models.CASCADE,null=True,blank=True)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.active and (self.valid_from <= now) and (self.valid_to is None or now <= self.valid_to) and (self.usage_limit is None or self.used_count < self.usage_limit)


class SaveCoupon(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username