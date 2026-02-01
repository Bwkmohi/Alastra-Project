from django.contrib import admin
from .models import CostFeeSite,WebsiteCostFeeTransaction,WebsiteWallet

admin.site.register(CostFeeSite)
admin.site.register(WebsiteCostFeeTransaction)
admin.site.register(WebsiteWallet)