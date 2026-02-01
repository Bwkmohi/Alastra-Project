from django.contrib import admin
from .models import GalleryProducts,GalleryItem


class GalleryItemInline(admin.TabularInline):
    model = GalleryItem
    extra = 1
    

@admin.register(GalleryProducts)
class AdminModel(admin.ModelAdmin):
    inlines = [GalleryItemInline]