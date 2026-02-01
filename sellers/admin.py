from django.contrib import admin
from .models import Seller ,Shop,ShopRate


class ShopAdmin(admin.ModelAdmin):
    list_display = ('name_shop','active','created',)
    list_filter = ['active','created',]
admin.site.register(Shop,ShopAdmin)


class SellerAdmin(admin.ModelAdmin):

    list_display = ('user','user_authentication','created',)
    list_filter = ['created','user_authentication']
admin.site.register(Seller,SellerAdmin)


admin.site.register(ShopRate)