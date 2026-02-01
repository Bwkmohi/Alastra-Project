from django.contrib import admin
from .models import  MonthlyProfit,ProductPriceHistory

admin.site.register(ProductPriceHistory)
admin.site.register(MonthlyProfit)