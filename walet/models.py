from django.db import models
from accaunts.models import UserAuthentication
from shop.models import to_persian_number



class Wallet(models.Model):
    """
    Docstring for Wallet
    """

    user = models.ForeignKey(UserAuthentication,on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f'{self.user.user.username} - {self.balance}'
 

class BankCartNumber(models.Model):
    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return self.number


class Transaction(models.Model):
    TRANSACTION_TYPE = [
       ('pending', 'Pending'),
        ('deposit', 'واریز'),
        ('withdraw', 'برداشت'),
        ('payment', 'پرداخت'),
        ('payment_by_others', 'پرداخت از طریق دیگران'),
    ]

    wallet = models.ForeignKey(Wallet,on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=130)
    transaction_type = models.CharField(max_length=1000,choices=TRANSACTION_TYPE)
    authority = models.CharField(max_length=100, null=True, blank=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.BooleanField(default=False) #true =  موفقیت امیز
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.wallet.user.user.username} - {self.amount}'
    
    def to_persian_amount_number(self):
        return to_persian_number(self.amount)