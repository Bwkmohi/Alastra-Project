from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Avg
   


class BrandCategory(models.Model):
   name = models.CharField(max_length=50)
   icon = models.CharField(max_length=50,null=True,blank=True)
   slug = models.SlugField(blank=True, null=True,unique=True)
   image = models.ImageField(upload_to='media/brand_images',null=True,blank=True)
   description = models.CharField(max_length=70,null=True,blank=True)

   def __str__(self):
      return self.name
   
 

class ColorCategory(models.Model):
   name = models.CharField(max_length=50)
   color_grb = models.CharField(max_length=70,default='#',null=True,blank=True)

   def __str__(self):
      return self.name



class Products(models.Model):
      name = models.CharField(_('نام  '),max_length=20)
      description = models.TextField(_('توضیحات'),)
      image = models.ImageField(_('1  575x575-عکس'),upload_to='media/product_images')
      price = models.IntegerField(_('قیمت'))
      sell_price = models.IntegerField(null=True,blank=True)
      description_seo = models.CharField(_('توضیحات سئو سایت'),max_length=80, null=True,blank=True)
         
      category = models.ForeignKey('SuperCategory',on_delete=models.CASCADE,null=True,blank=True)
      main_cattegory = models.ManyToManyField('MainCategory')
      color = models.ForeignKey(ColorCategory,on_delete=models.CASCADE,null=True,blank=True)
      brand = models.ForeignKey(BrandCategory,on_delete=models.CASCADE,null=True,blank=True)
      slug = models.SlugField(blank=True, null=True,unique=True)
      qunat = models.IntegerField(verbose_name='تعداد موجود ', blank=True,null=True) 
      is_sellprice = models.BooleanField( default=False,verbose_name='ایجاد تخفیف ویزه')
      spessial = models.BooleanField(default=False,verbose_name='ایجاد محصول ویزه')
      shop = models.ForeignKey('sellers.Shop',on_delete=models.CASCADE)
      views = models.IntegerField(default=0) 
      active = models.BooleanField(default=True)
      have = models.BooleanField(default=True)
      like = models.ManyToManyField(User,null=True,blank=True)
      created = models.DateTimeField(auto_now_add=True)
 
      class Meta:
        verbose_name = " محصولات"
        verbose_name_plural = "همه محصولات"
      
      def __str__(self):
         return self.name
      
      def price_(self):
         if self.sell_price:
            return self.sell_price
         else:
            return self.price

      def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk,self.slug])

      def product_like(self):
         list_like=[].append(
            Products.objects.get(
                  id = self.pk
            ).like
         )
         return len(list_like)
      
      def description_(self):
         return self.description[:45] + '...'
 
      def comments_count(self):
         return Comments.objects.filter(product=self).count()
 
      def total_rates(self):
         comments = Comments.objects.filter(product=self)
         avg_rating = comments.aggregate(Avg('rating'))['rating__avg']
         if avg_rating is not None:
            res = round(avg_rating, 2)
            # res_persian = to_persian_number(res)
            return res
         return 0
         # return '۰' 
      

      def total_sale(self):
         from reservations.models import Reservation
         return Reservation.objects.filter(product=self,paid=True).count()
      


def to_persian_number(number):
    persian_digits = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
                      '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    return ''.join(persian_digits.get(ch, ch) for ch in str(number))


class ProductKeyValues(models.Model):
   product = models.ForeignKey(Products,on_delete=models.CASCADE,related_name='details')
   key = models.ForeignKey('ProductDetaKeys',on_delete=models.CASCADE,null=True,blank=True) 
   value = models.CharField(max_length=200)

   def __str__(self):
      if self.key and self.value:
         return f'{self.key.key} - {self.value}'
      else:
         return self.product.name



class ProductDetaKeys(models.Model):
   category = models.ForeignKey('SuperCategory',on_delete=models.CASCADE)
   key = models.CharField(max_length=200)
   icon = models.CharField(max_length=200,null=True,blank=True)

   def __str__(self):
      return self.key
 


class Comments(models.Model):
   product = models.ForeignKey(Products,related_name='product',verbose_name='محصول مورد نظر',on_delete=models.CASCADE)
   user = models.ForeignKey(User,on_delete=models.CASCADE)
   message = models.TextField(max_length=320,verbose_name='متن')
   rating = models.IntegerField(default=5)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.user.first_name
       
   def message_(self):
      return self.message[:105]

   def total_rates(self):
      comments = Comments.objects.filter(product=self.product)
      avg_rating = comments.aggregate(Avg('rating'))['rating__avg']
      if avg_rating is not None:
         return round(avg_rating, 2)  
      return 0   

      
         
class SuperCategory(models.Model):
   name = models.CharField(max_length=50)
   slug = models.SlugField(unique=True)
   icon = models.CharField(max_length=100, null=True, blank=True)
   image = models.ImageField(upload_to='media/product_category_images')
   short_des = models.CharField(max_length=50, blank=True, null=True)

   def __str__(self):
      return self.name
    
   def get_main_categories(self):
      try:
         SuperCategory.objects.get(id=self.pk)
         return MainCategory.objects.filter(super_category__id=self.pk)
      except SuperCategory.DoesNotExist:
         return None
         

   class Meta:
      verbose_name = "دسته‌بندی اصلی"
      verbose_name_plural = "دسته‌بندی‌های اصلی"



class Category(models.Model):
   name = models.CharField(max_length=55)
   description = models.CharField(max_length=200,null=True,blank=True)
   slug = models.SlugField(unique=True,null=True,blank=True)

   def __str__(self):
      return self.name

   class Meta:
      verbose_name = "دسته‌بندی گروهی"
      verbose_name_plural = "دسته‌بندی‌های گروهی"



class MainCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True,null=True,blank=True)
    super_category = models.ForeignKey(SuperCategory, on_delete=models.CASCADE, related_name='main_categories',null=True,blank=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='main_categories')  
    image = models.ImageField(upload_to='media/product_category_images') 
    icon = models.CharField(max_length=100, null=True, blank=True)
    short_des = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "دسته‌بندی میانی"
        verbose_name_plural = "دسته‌بندی‌های میانی"
