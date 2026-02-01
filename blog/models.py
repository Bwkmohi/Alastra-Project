from django.db import models
from accaunts.models import UserAuthentication,NationalIDAuthentication
from django.utils.text import slugify



class AuthorModel(models.Model):
    full_name = models.CharField(max_length=30)
    profile = models.ImageField(upload_to='media/author_profile',null=True,blank=True)
    user_authentication = models.ForeignKey(UserAuthentication,on_delete=models.CASCADE)
    national_ID_authentication = models.ForeignKey(NationalIDAuthentication,on_delete=models.CASCADE,null=True,blank=True)
    biographi = models.TextField(null=True,blank=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_authentication.user.username
    
    def count_posts(self):
        return BlogPost.objects.filter(author=self,active=True).count()




 
class BlogPost(models.Model):
    title = models.CharField(max_length=40)
    author = models.ForeignKey(AuthorModel,on_delete=models.CASCADE)
    short_des = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='media/post_image',null=True,blank=True)
    slug = models.SlugField(unique=True,null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    time_red = models.IntegerField(null=True,blank=True,default=5)
    views = models.IntegerField(default=0)
    category = models.ForeignKey('CategoryBlog',on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=True)
 

    def __str__(self):
        # if not self.slug:
        #     self.slug = self.title
        #     self.save()
        return self.title
            
    # def save(self, *args, **kwargs):
    #     # استفاده از slugify برای ایجاد اسلاگ
    #     self.slug = slugify(self.title)
    #     super().save(*args, **kwargs)

class BlogContents(models.Model):
 
    post = models.ForeignKey(BlogPost,on_delete=models.CASCADE)
    title = models.CharField(max_length=140,null=True,blank=True)
    content = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='media/post_content_image',null=True,blank=True)

    def __str__(self):
        return f'{self.title} - {self.post.title} '
 
 
 
class CategoryBlog(models.Model):
    slug = models.SlugField(blank=True, null=True,unique=True)
    name = models.CharField(max_length=70)