from django.db import models
from django.contrib.auth.models import User
from cart.models import Cart

 

class GroupCart(models.Model):
    group_name = models.CharField(max_length=30)
    admin = models.ForeignKey(User,on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='group_carts')
    carts = models.ManyToManyField(Cart, related_name='group_carts')

    def total_prices(self):
        return sum([cart.self_cart_total_price() for cart in Cart.objects.filter(id__in=self.carts.all())])

    def get_products(self):
        return self.carts.all()

    def get_carts(self):
        return Cart.objects.filter(id__in=self.carts.all())

    def __str__(self):
        return self.group_name