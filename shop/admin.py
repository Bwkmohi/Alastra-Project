from django.contrib import admin
from .models import Products,Comments,BrandCategory,ColorCategory
from.models import Category,MainCategory,SuperCategory,ProductKeyValues,ProductDetaKeys

admin.site.site_header = "مدیریت فروشگاه Alastra"
admin.site.site_title = "مدیریت Alastra"
admin.site.index_title = "داشبورد مدیریت"
 
admin.site.register(ColorCategory)
admin.site.register(Category)
admin.site.register(BrandCategory)
admin.site.register(ProductDetaKeys)
admin.site.register(ProductKeyValues)


class CommentsAdmin(admin.ModelAdmin):
    list_display = ('user','rating','created_at','product')
    list_filter = ['user','rating','created_at','product']
admin.site.register(Comments,CommentsAdmin)
 
 
class MainCategoryAdmin(admin.TabularInline):
    model = MainCategory


@admin.register(SuperCategory)
class SuperCategoryAdmin(admin.ModelAdmin):
    inlines = [MainCategoryAdmin]

  
class ProductItemsAdmin(admin.TabularInline):
    model = ProductKeyValues


@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','qunat','color','created',)
    inlines = [ProductItemsAdmin]
