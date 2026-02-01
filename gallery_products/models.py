from django.db import models
from shop.models import Products
from sellers.models import Shop


class GalleryProducts(models.Model):
   product = models.ManyToManyField(Products)
   shop = models.ForeignKey(Shop,on_delete=models.CASCADE,null=True,blank=True)

   def __str__(self):
      return f'{self.shop.name_shop}'
   

class GalleryItem(models.Model):
   gallery_product = models.ForeignKey(GalleryProducts,on_delete=models.CASCADE)
   image = models.ImageField(upload_to='media/gallery_product')

   def __str__(self):
      return f'{self.pk}'
   
   def slug(self):
      for i in self.gallery_product.product.all():
         return i.slug
      
   def id_(self):
      for i in self.gallery_product.product.all():
         return i.pk