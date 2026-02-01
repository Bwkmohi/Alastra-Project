from django.db import models
from django.contrib.auth.models import User
from reservations.models import OrderModel


class CostFeeSite(models.Model):
    TYPE = [
        ('cost','cost'),
        ('fee','fee'),
        ('sent_cost','sent_cost')
    ]
    title = models.CharField(max_length=20,null= True,blank=True,default='هزینه ارسال',unique=True)
    is_percent = models.BooleanField(default=False,verbose_name='درصدی است')
    value = models.IntegerField(verbose_name='مقدار')
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.is_percent == True:
            syn = '%'
        else:
            syn = 'تومان'

        return f'{self.value}{syn}'


class WebsiteCostFeeTransaction(models.Model):
    amount = models.IntegerField()
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE,null=True,blank=True)
    cost_fee = models.ForeignKey(CostFeeSite,on_delete=models.CASCADE,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.amount} - {self.created}' if not self.description else f'Withdraw From Wallet - {self.amount}'
    
class WebsiteWallet(models.Model):
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return str(self.balance)