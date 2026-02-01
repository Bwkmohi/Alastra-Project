from django.db import models
from shop.models import Products


class Images(models.Model):
    IMAGE = [
        ('shop','shop'),
        ('authed_user','authed_user')
    ]

    GENDER = [
        ('MEN','MEN'),
        ('WOMEN','WOMEN')
    ]
    imgfor = models.CharField(max_length=100000,choices=IMAGE)
    gender = models.CharField(choices=GENDER,null=True,blank=True)
    image = models.ImageField(upload_to='media/supporter_user_image')

    def __str__(self):
        return self.imgfor
    


class MerchanteCode(models.Model):
    code = models.CharField(max_length=36)

    def __str__(self):
        return self.code
    



class SiteInfo(models.Model):
    email = models.EmailField(max_length=90)
    site_title = models.CharField(max_length=20,null=True,blank=True,default='Alastra')
    persian_site_title = models.CharField(max_length=20,null=True,blank=True)
    web_header = models.ImageField(upload_to='media/web_header',null=True,blank=True)
    web_header_style_class = models.CharField(max_length=200,default='h-10 w-32',null=True,blank=True,help_text='w=عرض. h=ارتفاع.')
    favicon = models.ImageField(upload_to='media/web_favicon',null=True,blank=True)
    description = models.TextField(max_length=100,null=True,blank=True)
    instagram_url = models.URLField(null=True,blank=True)
    telegram_url = models.URLField(null=True,blank=True)
    whatsapp_url = models.URLField(null=True,blank=True)
    twitter_url = models.URLField(null=True,blank=True)
    linkdn_url = models.URLField(null=True,blank=True)
    
    def __str__(self):
        return self.site_title or ''


class SymbolOfTrust(models.Model):
    image = models.ImageField(upload_to='media/symbol_of_trust_image')
    url = models.URLField()
    title = models.CharField(max_length=50,default='امنیت خرید شما، اولویت ماست')



class SeoWebSite(models.Model):
    PAGES = [
        ('shop','shop'),
        ('products','products'),
        ('category','category'),
        ('blogs','blogs'),
    ]
    page = models.CharField(max_length=100,choices=PAGES)
    title = models.CharField(
        max_length=65,
        help_text="""نام وب سایت | معرفی محصول.   مثال:  فهرست محصولات لپ‌تاپ، کامپیوتر و لوازم جانبی با بهترین کیفیت و قیمت."""
    )
    # default_image = ''
    description = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.page} -> {self.title}'
    


class PromotionalCardProduct(models.Model):
    name = models.CharField(max_length=70,null=True,blank=True)
    description = models.TextField(max_length=500,null=True,blank=True)
    product = models.ForeignKey(Products,on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name
    


class PromotionalProductsSlide(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    name = models.CharField(max_length=70,null=True,blank=True)
    description = models.TextField(max_length=500,null=True,blank=True)
    def __str__(self):
        return self.product.name