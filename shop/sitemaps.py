from django.contrib.sitemaps import Sitemap
from .models import Products,MainCategory,BrandCategory
from blog.models import BlogPost

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Products.objects.filter(active=True)

    def location(self, obj):
        return f"/product/{obj.id}/{obj.slug}/"  # یا هر URL که برای دیتیل داری


class ProductBrandSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return BrandCategory.objects.all()

    def location(self, obj):
         return f"/brand_detail/{obj.id}/{obj.slug}/"


class ProductMainCategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return MainCategory.objects.all()

    def location(self, obj):
        return f"/main_category_detail/{obj.slug}/"


class BlogSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return BlogPost.objects.filter(active=True)

    def location(self, obj):
        return f"/blogs/blog_detail/{obj.id}/"