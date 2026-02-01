from django.db import models



class Project(models.Model):
    domain = models.URLField(max_length=2000)
    name = models.CharField(max_length=200)
    alt = models.CharField(max_length=200)
    slug= models.SlugField(unique=True)
    url_domain = models.URLField()
    image = models.ImageField(upload_to='test/Project_image')
    desc = models.TextField(max_length=500)


class ProjectFiles(models.Model):
    name = models.CharField(max_length=200)
    des = models.TextField(max_length=400)
    file = models.FileField(upload_to='test/files')


class Conactions(models.Model):
    url = models.CharField(max_length=400)
    icon = models.CharField(max_length=200)


class DemoVideos(models.Model):
    video = models.FileField(upload_to='test/DemoVideos', null=True, blank=True)


class DemoPhotoGraphs(models.Model):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='test/DemoPhotoGraphs')
    alt = models.CharField(max_length=200,null=True,blank=True)
    url = models.URLField()


class PowerFullSeo(models.Model):
    title = models.CharField(max_length=200)
    des = models.TextField(max_length=4000)
    keyword = models.TextField(max_length=4000)
    
    def __str__(self):
        return self.title


class OgPowerFullSeo(models.Model):
    title = models.CharField(max_length=200)
    des = models.TextField(max_length=4000)
    keyword = models.TextField(max_length=4000)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='test/OgPowerFullSeo')
    
    def __str__(self):
        return self.title