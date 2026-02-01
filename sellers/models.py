from django.db import models
from django.contrib.auth.models import User
from accaunts.models import UserAuthentication
from shop.models import Products
from reservations.models import Reservation
from django.db.models import Avg,Sum


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_authentication = models.OneToOneField(UserAuthentication,on_delete=models.CASCADE)
    # national_id_auth = models.ForeignKey(NationalIDAuthentication,on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


 
class Shop(models.Model) :
    name_shop = models.CharField(max_length=26)
    description = models.CharField(max_length=120)
    logo = models.ImageField(upload_to='media/shop_logo',null=True,blank=True)
    banner = models.ImageField(upload_to='media/banner',null=True,blank=True)
    seller = models.ForeignKey(Seller,on_delete=models.CASCADE,related_name='shops')
    reported = models.BooleanField(default=False)
    active = models.BooleanField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name_shop
    
    def description_(self):
        return self.description[:26]
    
    def rateing(self):
        try:
            sr=ShopRate.objects.filter(reserv__shop = self)
            if sr.exists():
                return sr.first().shop_rate()
            return 0
        except ShopRate.DoesNotExist:
            return 0

    def shop_products_count(self):
        return Products.objects.filter(shop__id=self.pk,active = True).count()

    def shop_followers_count(self):
        from follow.views import count_followers
        return count_followers(self,self.pk)

    def shop_total_orders(self):
        return Reservation.objects.filter(shop=self).count()


    def shop_profit(self):
        return Reservation.objects.filter(shop=self,paid=True).aggregate(total=Sum('totalprice'))['total'] or 0

class ShopRate(models.Model):
    reserv = models.ForeignKey(Reservation,on_delete=models.CASCADE,null=True,blank=True)
    rateing = models.IntegerField()

    def __str__(self):
        return f'{self.rateing}'

    def shop_rate(self):
        average_rating = ShopRate.objects.filter(reserv__shop=Shop.objects.get(id=self.reserv.shop.pk)).aggregate(Avg('rateing'))['rateing__avg']
        return round(average_rating or 0, 1)