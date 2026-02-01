from django.contrib.sitemaps import Sitemap
from .models import Project

class ProjectSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return f"/adv/project_detail/{obj.id}/{obj.slug}/"  

