from django.db import models
from django.contrib.auth.models import User



class ProvinceCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



class Citys(models.Model):
    name = models.CharField(max_length=70)

    def __str__(self):
        return self.name



PAYMENT_METHOD = [
    ('WALLET', 'WALLET'),
    ('ZARRINPAL', 'ZARRINPAL')
]


class OrderModel(models.Model):
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=20)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    email = models.EmailField(max_length=40)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    paid = models.BooleanField(default=False)
    province = models.ForeignKey(ProvinceCategory,on_delete=models.CASCADE)
    city = models.ForeignKey(Citys,on_delete=models.CASCADE)
    postaddress = models.CharField(max_length=20)
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='کد رهگیری')
    total_price = models.IntegerField()
    payment_method = models.CharField(max_length=100,choices=PAYMENT_METHOD)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}'
    
    def get_total_price(self):
        return self.total_price
    
    def address_(self):
        return self.address[:40]



class Reservation(models.Model):    
    order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, verbose_name='سفارش')
    product = models.ForeignKey('shop.Products', on_delete=models.CASCADE, related_name='reservations')
    quantity = models.PositiveIntegerField()
    totalprice = models.DecimalField(max_digits=10, decimal_places=2)
    #   
    preparation = models.BooleanField(default=False)
    sent_to_post = models.BooleanField(default=False)
    post_delivery = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    # 
    canceled = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    shop = models.ForeignKey('sellers.Shop', on_delete=models.CASCADE)
    payment_method = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=PAYMENT_METHOD
    )
    tracking_code = models.CharField(max_length=100, null=True, blank=True, verbose_name='کد رهگیری')

    def __str__(self):
        return f"Reservation {self.id} for Order {self.order.id}"