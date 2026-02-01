from django.db import models
from django.contrib.auth.models import User
from shop.models import Products
from copon2.models import Coupon
from decimal import Decimal

#    قبل تحفیف همه چی محاسبه شده است
#   و در محاسبه از قبل مشخص شده که اگر از قبل ک.پن استفاده شده بود فعالش نکن
#    مثل چرخه بی پیان که چند قدم جلوترن



class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    use_coupon_code = models.ForeignKey(Coupon,on_delete=models.CASCADE,null=True,blank=True)
    coupon_applyed = models.BooleanField(default=False)
    total_price = models.IntegerField(default=0,null=True,blank=True)
    # total_price_after_applyed_coupon = models.IntegerField(default=0,null=True,blank=True)

    def __str__(self):
        return f'{self.user.username} - {str(self.cart_total_price())}'

    def cart_quantity(self):
        list_qty = []
        for item in Cart.objects.filter(user=self.user):list_qty.append(item.quantity) 
        return sum(list_qty)


    def cart_total_price(self):
        list_total_price = []
        for item in Cart.objects.filter(user=self.user):
            if not item.use_coupon_code and item.coupon_applyed == False:
                item.total_price = self.self_cart_total_price()

            else:
                if item.use_coupon_code.is_percent == True:
                    result = (Decimal(item.use_coupon_code.value) / Decimal(100)) * item.self_cart_total_price()
                    item.total_price = item.self_cart_total_price() - max(result, Decimal(0))
                    item.save()

                elif item.use_coupon_code.is_percent == False:
                    result = item.self_cart_total_price() - max(item.use_coupon_code.value, Decimal(0))
                    item.total_price = result
                    item.save()

            list_total_price.append(item.total_price)
        return sum(list_total_price)


    def self_cart_total_price(self):
        return Decimal(self.quantity) * Decimal(self.product.price_())



    # برای cart2.html ساخته شده و 
    def is_cart_use_coupon(self):
        cart_data = False

        for item in Cart.objects.filter(user = self.user):
            if item.use_coupon_code:
                cart_data={
                    'total_price':item.cart_total_price(),
                    'coupon':item.use_coupon_code,
                    'applyed':item.coupon_applyed,
                }
            else:cart_data = {'total_price':item.cart_total_price(),}
        return cart_data
