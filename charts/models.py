from django.db import models


class MonthlyProfit(models.Model):
    shop = models.ForeignKey('sellers.Shop',on_delete=models.CASCADE,related_name='charts_monthlyprofits')
    year = models.IntegerField()
    month = models.IntegerField()
    total_profit = models.FloatField(default=0)

    class Meta:
        unique_together = ('shop', 'year', 'month')

    def __str__(self):
        return f"{self.shop} - {self.year}/{self.month}: {self.total_profit}"


class ProductPriceHistory(models.Model):
    product = models.ForeignKey('shop.Products', on_delete=models.CASCADE, related_name='price_history')
    shop = models.ForeignKey('sellers.Shop', on_delete=models.CASCADE)
    price = models.FloatField()
    date = models.DateField()

    class Meta:
        unique_together = ('product', 'shop', 'date')  

    def __str__(self):
        return f"{self.product.name} - {self.date} - {self.price} تومان"