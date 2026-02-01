from django.db import models
from shop.models import Products
from sellers.models import Shop

class ProductVideo(models.Model):
    shop = models.ForeignKey(Shop,on_delete=models.CASCADE,null=True,blank=True)
    products = models.ManyToManyField(Products)
    title = models.CharField(max_length=30, blank=True, help_text="عنوان ویدیو ")
    video_file = models.FileField(upload_to='media/product_videos')   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" - {self.title}"    